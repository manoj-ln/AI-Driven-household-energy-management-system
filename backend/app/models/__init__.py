"""
Reserved for persistence/domain entities.

This package previously held three Pydantic classes (EnergyRecord,
PredictionResult, User) that duplicated definitions living elsewhere and
were never actually imported by any route or service - dead code, not a
real "models" layer. They've been removed:

- EnergyRecord  -> superseded by app.schemas.energy_schema.EnergyReading,
                   which is now the real request model used by the API.
- PredictionResult -> had no consumer; prediction_service.py returns plain
                   dicts today. Worth revisiting once the ML pipeline gets
                   its own dedicated cleanup pass (see recommendations) -
                   changing that return contract touches every caller, so
                   it wasn't bundled into this structural pass.
- User          -> had a `role` field sketched out for RBAC that was never
                   wired to anything. That field now lives on the real user
                   record in app.services.auth_service.AuthService instead
                   (additive, defaults to "user" for existing accounts).

This package is kept (rather than deleted outright) as the intended home
for real ORM/persistence entities if/when the project migrates
`app/database` from raw sqlite3 to SQLAlchemy (see recommendations) -
`schemas/` stays API I/O contracts, `models/` becomes the ORM/domain layer.
"""
