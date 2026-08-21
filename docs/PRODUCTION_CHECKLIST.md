# Production Readiness Checklist

## Security
- Set `AUTH_SECRET_KEY` to a strong random value in deployment (never keep default).
- Restrict `CORS_ALLOWED_ORIGINS` to your real frontend domains.
- Serve backend behind HTTPS reverse proxy (Nginx/Caddy/Cloud LB).
- Rotate auth secrets periodically and after suspected exposure.
- Monitor failed login attempts and add account lock/rate limiting if needed.

## Backend Reliability
- Run migrations before startup if using schema changes.
- Set process manager (systemd, PM2, Docker restart policy) for auto-restart.
- Enable structured logs and centralized error tracking.
- Configure backup for `backend/data/` if persistence is required.

## Frontend Reliability
- Build with `npm run build` and deploy static assets via CDN/web server.
- Keep environment-specific API URL in `.env.production`.
- Validate browser console has no runtime errors in core screens.

## Quality Gates
- CI passes backend tests and frontend build on every PR.
- Manual smoke test completed:
  - login/register
  - dashboard analytics
  - predictions + explainability
  - dataset mode/file selection
  - optimization report

## Documentation
- Keep README metrics and dataset list up to date.
- Keep architecture statement consistent: modular service-oriented backend.
