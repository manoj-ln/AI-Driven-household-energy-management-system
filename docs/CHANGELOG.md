# Changelog

Tracks the module-by-module improvement pass requested for this project.
Each phase is scoped, verified, and committed separately so changes stay
reviewable instead of arriving as one large, unauditable rewrite.

## Phase 1 - Project Structure & Database Consolidation

**Scope:** sections 1 (Project Structure) and 2 (Database Structure) of the
improvement plan, plus the minimum of sections 6/7 (security/env config)
needed as a foundation - config.py and .env.example - since later phases
depend on them existing.

### Database layer
- Replaced three coexisting implementations
  (`db.py`, `db_new.py`, `simple_db.py`) with one:
  `connection.py` (connection factory) + `schema.py` (DDL) +
  `repository.py` (`EnergyRepository`, exported as `db`) + `init_db.py`
  (standalone setup script).
- `db_new.py` and `simple_db.py` were confirmed dead code (zero imports
  anywhere in the app) before deletion. `db_new.py` additionally contained
  a bug in `get_energy_stats` (`end_date.replace(hour=end_date.hour - hours)`,
  which raises `ValueError` once `hours` exceeds the current hour) that had
  never been caught because nothing imported the file.
- Added indexes on `energy_readings(timestamp)`, `energy_readings(device_id)`,
  and `chatbot_messages(session_id)` - the columns every existing query
  filters/sorts on.
- `DATABASE_PATH` env var now controls the SQLite file location (falls back
  to the original hardcoded path if unset, so existing setups are unaffected).

### Bug fix: `POST /energy/ingest`
- Was raising `KeyError('device_id')` on every call, regardless of payload,
  because `EnergyReading.dict()` never produced the `device_id`/`device_type`
  keys that `insert_reading` requires.
- Fixed by converting `EnergyReading` to a real Pydantic model (proper
  request validation + OpenAPI schema, instead of the route accepting an
  unvalidated raw `dict`) and having `DataService.save_reading` map fields
  onto the datastore's column names explicitly.

### Dead code removed
- `brain/` - a leftover AI-agent scratch directory (172K, ~34 files),
  unrelated to the application, zero references from app code.
- `app/models/energy.py`, `app/models/prediction.py`, `app/models/user.py` -
  zero imports anywhere. The `role` field sketched in the unused `User`
  model was preserved by moving it into the real user record in
  `auth_service.py` instead (additive; defaults to `"user"` for accounts
  created before this change).
- `core/config.py` and `core/security.py` were unused placeholders; both
  are now real (central settings; a shared `get_current_user` dependency
  that replaced duplicated bearer-token-parsing logic in `routes/users.py`).
- Confirmed-unused imports removed from `mqtt_service.py`,
  `prediction_service.py`, `scripts/build_cache.py`,
  `models/training/preprocess.py`, `models/training/train.py`.

### Structure
- `database/manual_input.py` (business logic, not data-access code) moved
  to `services/manual_input_service.py`.
- Root-level docs (`RUN_PROJECT.md`, `PRODUCTION_CHECKLIST.md`,
  `MANUAL_DATA_INPUT_README.md`, `OUTPUT_STEPS.md`,
  `COST_VERIFICATION_LOG.md`) moved into `docs/`, with a `docs/README.md`
  index. `README.md` stays at the root.
- Added `.env.example` documenting every environment variable the app
  actually reads.

### Verification
No network access in this environment to `pip install`/`npm install`, so
nothing here could be run through a live `uvicorn`/`pytest`/`npm test`.
Verified instead by: a full `py_compile` sweep of the backend, an
AST-based unused-import scan, and functional smoke tests run for real
against the actual source files - the SQLite repository layer (insert/
query/update/delete), the auth + role flow (including backward
compatibility with pre-existing user records that predate the `role`
field), and the `/energy/ingest` fix (via a minimal stdlib-only stand-in
for `pydantic`, since the real package isn't installed here).
**Recommended before deploying:** run the existing `pytest` suite and boot
the server locally to confirm end-to-end behavior.

### Deliberately not changed in this phase
- `/energy`, `/control`, and `/predictions` routes still have no
  authentication. Applying `get_current_user` to them is a real behavior
  change (the frontend would need to start sending a token), so it's
  scoped into the security-hardening phase instead of bundled here.
- No SQLAlchemy migration, despite `sqlalchemy`/`alembic` sitting unused in
  `requirements.txt`. The current raw-sqlite3 implementation was
  reorganized, not replaced - a full ORM migration touches every service
  that reads `app.database.repository`, and isn't something to do blind in
  an environment where it can't be executed and tested live.
