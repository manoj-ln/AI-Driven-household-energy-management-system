"""
Pydantic schema for the /energy endpoints.

`EnergyReading` used to be a hand-rolled class (no validation, no OpenAPI
schema, just a plain __init__ + .dict()), and `POST /energy/ingest` took a
raw `dict` request body instead of this model - so FastAPI never validated
incoming requests at all. Malformed input reached `datetime.fromisoformat()`
/ `float()` directly and surfaced as an opaque 400 with the raw Python
exception string.

This also fixes a real pre-existing bug: the old EnergyReading.dict() only
ever produced {timestamp, energy_kwh, appliance, location}, but
EnergyRepository.insert_reading requires `device_id` and `device_type` keys
(bracket access, not .get()) to insert a row - so every single call to
POST /energy/ingest raised `KeyError: 'device_id'` inside DataService.save_reading,
regardless of what the caller sent. See DataService.save_reading for the fix
(it now maps this schema's fields onto the datastore's column names
explicitly, instead of assuming `.dict()` output lines up with SQL columns).

`app/models/energy.py` defined an equivalent but unused `EnergyRecord` model
(never imported anywhere); its fields are folded in here instead of keeping
two near-identical definitions around.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class EnergyReading(BaseModel):
    """Request body for POST /energy/ingest."""

    timestamp: datetime
    energy_kwh: float
    device_id: str = "manual_entry"
    device_type: Optional[str] = None
    appliance: Optional[str] = None
    location: Optional[str] = None
    temperature: Optional[float] = None
