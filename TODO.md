# SentinelAI - Deployment Tasks (Render Full-Stack - Option A)

## Objective
Deploy SentinelAI as a single full-stack service on Render.com that serves both the FastAPI backend AND the built React frontend on the same origin (satisfying the `/api` and `/ws` same-origin constraint).

## Approach
This is a **full-stack application** where the frontend calls `/api/...` and connects to `/ws` using the same host. Render can host a single Python web service that:
1. Runs the FastAPI backend
2. Mounts the built `frontend/dist/` as static files with SPA fallback
3. Serves both on the same origin

## Steps
- [x] 1. Verify Docker/WSL blocker (Docker path blocked - requires WSL2 admin install + restart)
- [x] 2. Pivot to cloud deployment (Option A - Render full-stack)
- [x] 3. Verify Vercel CLI authenticated (gauravk0001)
- [x] 4. Frontend dependencies installed (npm ci)
- [x] 5. Frontend build verified (dist/index.html + dist/assets created)
- [x] 6. Modify backend `app.py` to serve static frontend files (SPA fallback)
- [x] 7. Create Render Dockerfile (`Dockerfile.render`) for full-stack service
- [x] 8. Create `render.yaml` blueprint
- [x] 9. Update `.gitignore` to exclude build artifacts
- [x] 9b. Clean up requirements.txt (remove unused heavy deps: weasyprint, slowapi, prometheus, reportlab)
- [x] 10. Re-authenticate GitHub CLI (token invalid) - logged in as Gauravk0001
- [ ] 11. Push code to GitHub repo (Sentinel-ai.git)
- [ ] 12. Create Render service via blueprint or dashboard
- [ ] 13. Verify deployment (health, login, AI endpoints)

## Notes
- Default users: admin/admin123, analyst/analyst123, compliance/compliance123, viewer/viewer123
- Backend uses SQLite by default (file-based, persists on Render disk)
- AI model retrains on first use
