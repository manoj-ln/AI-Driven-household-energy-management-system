"""
Authentication service using database-backed user storage.

Replaces the previous JSON-file based implementation with proper
database storage using the repository pattern.
"""

import base64
import hashlib
import hmac
import os
import re
import json
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from app.core.config import settings
from app.database.repository import db


class AuthService:
    _token_ttl_hours = 12
    _login_attempts: dict[str, dict] = {}
    _max_attempts = 5
    _attempt_window_seconds = 300
    _block_seconds = 300

    @classmethod
    def _token_secret(cls) -> str:
        return settings.auth_secret_key

    @staticmethod
    def _hash_password(password: str, salt: Optional[str] = None) -> str:
        salt = salt or secrets.token_hex(16)
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            120000,
        )
        return f"{salt}${digest.hex()}"

    @staticmethod
    def _verify_password(password: str, hashed_password: str) -> bool:
        if "$" not in hashed_password:
            return False
        salt, _ = hashed_password.split("$", 1)
        candidate = AuthService._hash_password(password, salt=salt)
        return hmac.compare_digest(candidate, hashed_password)

    @staticmethod
    def _b64url_encode(raw: bytes) -> str:
        return base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")

    @staticmethod
    def _b64url_decode(raw: str) -> bytes:
        padding = "=" * ((4 - len(raw) % 4) % 4)
        return base64.urlsafe_b64decode(raw + padding)

    @classmethod
    def _sign(cls, payload: str) -> str:
        signature = hmac.new(
            cls._token_secret().encode("utf-8"),
            payload.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return signature

    @classmethod
    def generate_token(cls, identifier: str) -> str:
        exp = datetime.now(timezone.utc) + timedelta(hours=cls._token_ttl_hours)
        payload = {"sub": identifier, "exp": exp.timestamp()}
        payload_encoded = cls._b64url_encode(json.dumps(payload).encode("utf-8"))
        signature = cls._sign(payload_encoded)
        return f"{payload_encoded}.{signature}"

    @classmethod
    def parse_token(cls, token: str) -> Optional[dict]:
        try:
            payload_encoded, signature = token.split(".", 1)
        except ValueError:
            return None
        if not hmac.compare_digest(signature, cls._sign(payload_encoded)):
            return None
        try:
            payload = json.loads(cls._b64url_decode(payload_encoded).decode("utf-8"))
        except (json.JSONDecodeError, ValueError):
            return None
        if float(payload.get("exp", 0)) < datetime.now(timezone.utc).timestamp():
            return None
        return payload

    @classmethod
    def _is_valid_identifier(cls, identifier: str) -> bool:
        value = str(identifier or "").strip().lower()
        return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value) or re.fullmatch(r"\d{10}", value))

    @classmethod
    def _is_strong_password(cls, password: str) -> bool:
        value = str(password or "")
        return (
            len(value) >= 8
            and bool(re.search(r"[A-Z]", value))
            and bool(re.search(r"[a-z]", value))
            and bool(re.search(r"\d", value))
        )

    @classmethod
    def _normalize_age(cls, age: str) -> str:
        value = str(age or "").strip()
        if not value.isdigit():
            return ""
        numeric = int(value)
        if numeric < 1 or numeric > 120:
            return ""
        return str(numeric)

    @classmethod
    def _normalize_name(cls, name: str) -> str:
        value = re.sub(r"\s+", " ", str(name or "").strip())
        if len(value) < 2 or len(value) > 60:
            return ""
        return value

    @classmethod
    def _track_login_failure(cls, identifier: str) -> None:
        now = datetime.now(timezone.utc).timestamp()
        key = str(identifier or "").strip().lower()
        entry = cls._login_attempts.get(key, {"count": 0, "first_at": now, "blocked_until": 0})
        if now - float(entry.get("first_at", now)) > cls._attempt_window_seconds:
            entry = {"count": 0, "first_at": now, "blocked_until": 0}
        entry["count"] = int(entry.get("count", 0)) + 1
        if entry["count"] >= cls._max_attempts:
            entry["blocked_until"] = now + cls._block_seconds
        cls._login_attempts[key] = entry

    @classmethod
    def _clear_login_failures(cls, identifier: str) -> None:
        key = str(identifier or "").strip().lower()
        if key in cls._login_attempts:
            del cls._login_attempts[key]

    @classmethod
    def _is_login_blocked(cls, identifier: str) -> bool:
        key = str(identifier or "").strip().lower()
        entry = cls._login_attempts.get(key)
        if not entry:
            return False
        now = datetime.now(timezone.utc).timestamp()
        return float(entry.get("blocked_until", 0)) > now

    @classmethod
    def register(cls, name: str, age: str, identifier: str, password: str) -> dict:
        normalized_name = cls._normalize_name(name)
        normalized_age = cls._normalize_age(age)
        if not normalized_name:
            return {"status": "error", "message": "Name should be 2-60 characters"}
        if not normalized_age:
            return {"status": "error", "message": "Age should be a valid number between 1 and 120"}
        if not cls._is_valid_identifier(identifier):
            return {"status": "error", "message": "Identifier must be a valid email or 10-digit phone number"}
        if not cls._is_strong_password(password):
            return {"status": "error", "message": "Password must be at least 8 chars with upper, lower, and number"}

        normalized_identifier = identifier.strip().lower()
        existing = db.get_user_by_identifier(normalized_identifier)
        if existing:
            return {"status": "error", "message": "Account already exists"}

        password_hash = cls._hash_password(password)
        try:
            user = db.create_user(
                identifier=normalized_identifier,
                name=normalized_name,
                age=normalized_age,
                password_hash=password_hash,
                role="user",
            )
        except Exception as e:
            return {"status": "error", "message": f"Registration failed: {str(e)}"}

        token = cls.generate_token(normalized_identifier)
        return {
            "status": "success",
            "token": token,
            "profile": {
                "name": normalized_name,
                "age": normalized_age,
                "identifier": normalized_identifier,
                "role": "user",
            },
        }

    @classmethod
    def login(cls, identifier: str, password: str) -> dict:
        normalized_identifier = identifier.strip().lower()
        if cls._is_login_blocked(normalized_identifier):
            return {"status": "error", "message": "Too many failed attempts. Please try again later."}

        user = db.get_user_by_identifier(normalized_identifier)
        if not user:
            cls._track_login_failure(normalized_identifier)
            return {"status": "error", "message": "Account not found"}
        if not cls._verify_password(password, str(user.get("password_hash", ""))):
            cls._track_login_failure(normalized_identifier)
            return {"status": "error", "message": "Invalid password"}

        cls._clear_login_failures(normalized_identifier)
        token = cls.generate_token(normalized_identifier)
        return {
            "status": "success",
            "token": token,
            "profile": {
                "name": user.get("name", ""),
                "age": user.get("age", ""),
                "identifier": normalized_identifier,
                "role": user.get("role", "user"),
            },
        }

    @classmethod
    def get_profile_from_token(cls, token: str) -> Optional[dict]:
        payload = cls.parse_token(token)
        if not payload:
            return None
        identifier = str(payload.get("sub", "")).lower()
        user = db.get_user_by_identifier(identifier)
        if not user:
            return None
        return {
            "name": user.get("name", ""),
            "age": user.get("age", ""),
            "identifier": identifier,
            "role": user.get("role", "user"),
        }

    @classmethod
    def update_profile(cls, identifier: str, name: str, age: str) -> dict:
        normalized_identifier = str(identifier or "").strip().lower()
        normalized_name = cls._normalize_name(name)
        normalized_age = cls._normalize_age(age)
        if not normalized_name:
            return {"status": "error", "message": "Name should be 2-60 characters"}
        if not normalized_age:
            return {"status": "error", "message": "Age should be a valid number between 1 and 120"}

        user = db.update_user_profile(
            identifier=normalized_identifier,
            name=normalized_name,
            age=normalized_age,
        )
        if not user:
            return {"status": "error", "message": "User not found"}
        return {
            "status": "success",
            "profile": {
                "name": user.get("name", ""),
                "age": user.get("age", ""),
                "identifier": normalized_identifier,
                "role": user.get("role", "user"),
            },
        }