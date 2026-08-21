"""
Shared authentication dependency for FastAPI routes.

Previously this file only held an unused `verify_token()` stub (checked a
literal `"secret-token"` string, was never imported anywhere), while the
*actual* auth check - "read the Authorization header, strip 'Bearer ', look
up the token" - was written out twice by hand inside
`routes/users.py` (once in `get_current_user`, once in `update_current_user`).

`get_current_user` below is that same logic, once, as a real FastAPI
dependency. Route handlers that need an authenticated user add one
parameter:

    from app.core.security import get_current_user

    @router.get("/something")
    async def handler(user: dict = Depends(get_current_user)):
        ...

Behavior is unchanged from the original inline code: missing/malformed
header -> 401 "Missing bearer token"; invalid/expired token -> 401 "Invalid
or expired token".

Note: `/energy`, `/control`, and `/predictions` do not apply this dependency
yet - those endpoints currently have no authentication at all. Wiring it in
is a real behavior change (any frontend calling them would need to start
sending a token), so it's deliberately left for the security-hardening pass
called out in recommendations rather than bundled into this structural
cleanup.
"""

from fastapi import Header, HTTPException

from app.services.auth_service import AuthService


async def get_current_user(authorization: str = Header(default="")) -> dict:
    """Resolve the bearer token in the Authorization header to a user profile.

    Raises HTTPException(401) if the header is missing/malformed or the
    token is invalid/expired.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.replace("Bearer ", "", 1).strip()
    profile = AuthService.get_profile_from_token(token)
    if not profile:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return profile
