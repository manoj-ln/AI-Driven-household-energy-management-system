from datetime import datetime

from typing import Any, Optional


def parse_timestamp(value: Any) -> datetime:
    """Parse an ISO-8601 timestamp string into a datetime.

    Handles the 'Z' UTC suffix and passes through already-parsed datetimes.
    """
    if isinstance(value, datetime):
        return value
    text = str(value)
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    return datetime.fromisoformat(text)


def format_energy(value: float) -> str:
    """Format an energy value as a human-readable kWh string."""
    return f"{value:.2f} kWh"
