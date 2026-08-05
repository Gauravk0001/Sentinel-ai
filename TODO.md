# SentinelAI - Run Locally

## Steps
- [x] 1. Analyze project structure & understand architecture
- [x] 2. Create backend Python virtual environment
- [x] 3. Install backend dependencies (relax versions if Python 3.14 incompatible)
- [x] 4. Build frontend (npm run build) -> frontend/dist
- [x] 5. Start backend server (uvicorn) serving full-stack on port 8000
- [x] 6. Verify /health, /api endpoints, and frontend at localhost:8000
- [x] 7. Provide access with default credentials

## Fix - AI Features Not Working
- [x] Diagnosed: /api/ai/alerts/live and /api/ai/high-risk took 83s (predict_all over 1000 employees)
- [x] Fixed: predict_all now reuses precomputed training results (fast path)
- [x] Verified: alerts/live 83s -> 0.1s, high-risk 0.1s, predict 0.1s, model-info 0s
- [x] Restarted backend to apply fix
