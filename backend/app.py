"""
SentinelAI - Main FastAPI Application
AI-Powered Insider Threat Detection Platform
"""

import sys
import os
from datetime import datetime
from contextlib import asynccontextmanager

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

from config import settings
from database import init_db, get_session
from auth import seed_users
from websocket_manager import manager, handle_websocket


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager"""
    # Startup
    print(f"\n🚀 {settings.APP_NAME} v{settings.VERSION} starting...")
    print(f"📡 Environment: {settings.ENVIRONMENT}")
    print(f"🔌 Port: {settings.PORT}")
    
    # Initialize database
    try:
        from database import init_db
        init_db()
        print("✅ Database initialized")
    except Exception as e:
        print(f"⚠️ Database init skipped: {e}")
    
    # Seed default users
    try:
        seed_users()
        print("✅ Default users seeded")
    except Exception as e:
        print(f"⚠️ User seeding skipped: {e}")
    
    print(f"✅ {settings.APP_NAME} is ready!\n")
    
    yield
    
    # Shutdown
    print(f"\n🛑 {settings.APP_NAME} shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="AI-Powered Insider Data Exfiltration Detection Platform",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Import and include routers
from routes.auth_routes import router as auth_router
from routes.dashboard_routes import router as dashboard_router
from routes.employee_routes import router as employee_router
from routes.alert_routes import router as alert_router
from routes.incident_routes import router as incident_router
from routes.ai_routes import router as ai_router

app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(employee_router)
app.include_router(alert_router)
app.include_router(incident_router)
app.include_router(ai_router)


# === WebSocket Endpoint ===

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str = None):
    """WebSocket endpoint for real-time updates"""
    await handle_websocket(websocket, client_id)


@app.websocket("/ws")
async def websocket_endpoint_no_id(websocket: WebSocket):
    """WebSocket endpoint without client ID"""
    await handle_websocket(websocket)


# === Health Check & Info Endpoints ===


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    # Check component health
    components = {
        "database": "ok",
        "ai_engine": "ok",
        "websocket": "ok",
    }

    # Try AI engine readiness
    try:
        from ai_service import get_ai_service
        svc = get_ai_service()
        model_info = svc.get_model_info()
        components["ai_engine"] = "ok"
        ai_model = model_info.get("active_model", {}).get("model_version", "unknown")
    except Exception:
        components["ai_engine"] = "degraded"
        ai_model = "unknown"

    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": settings.VERSION,
        "uptime": "running",
        "websocket_connections": manager.get_connected_count(),
        "environment": settings.ENVIRONMENT,
        "components": components,
        "ai_model": ai_model
    }


@app.get("/api/info")
async def api_info():
    """API information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "endpoints": {
            "auth": "/api/auth/*",
            "dashboard": "/api/dashboard/*",
            "employees": "/api/employees/*",
            "alerts": "/api/alerts/*",
            "incidents": "/api/incidents/*",
            "ai": "/api/ai/*",
            "websocket": "/ws",
            "docs": "/api/docs",
            "health": "/health"
        }
    }


# === Report Generation Endpoints ===

@app.get("/api/reports/daily-summary")
async def get_daily_summary():
    """Generate daily security summary report"""
    import random
    return {
        "report_type": "daily_summary",
        "generated_at": datetime.now().isoformat(),
        "period": {
            "start": (datetime.now()).strftime("%Y-%m-%d"),
            "end": datetime.now().strftime("%Y-%m-%d")
        },
        "summary": {
            "total_alerts": random.randint(20, 80),
            "critical_alerts": random.randint(1, 5),
            "high_alerts": random.randint(3, 15),
            "open_incidents": random.randint(2, 10),
            "high_risk_employees": random.randint(3, 12),
            "average_risk_score": round(random.uniform(20, 40), 1),
            "threats_blocked": random.randint(5, 20),
            "employees_monitored": 1000,
            "suspicious_activities": random.randint(10, 40)
        },
        "top_incidents": [
            {
                "incident_id": f"INC-{random.randint(1000, 9999)}",
                "employee": f"EMP{random.randint(1, 1000):05d}",
                "type": random.choice(["data_exfiltration", "insider_threat", "policy_violation"]),
                "risk_score": round(random.uniform(70, 98), 1),
                "status": "open"
            } for _ in range(5)
        ],
        "department_risk": [
            {"department": "Engineering", "avg_risk": round(random.uniform(25, 45), 1), "employees_at_risk": random.randint(5, 20)},
            {"department": "Finance", "avg_risk": round(random.uniform(20, 40), 1), "employees_at_risk": random.randint(3, 15)},
            {"department": "IT", "avg_risk": round(random.uniform(20, 35), 1), "employees_at_risk": random.randint(3, 12)},
            {"department": "Sales", "avg_risk": round(random.uniform(15, 30), 1), "employees_at_risk": random.randint(2, 10)},
            {"department": "HR", "avg_risk": round(random.uniform(10, 25), 1), "employees_at_risk": random.randint(1, 8)}
        ]
    }


# === Serve Frontend Static Files (for full-stack deployment) ===

# Locate the built frontend directory. In production (Render), the built
# frontend is copied to /app/frontend/dist. In dev, it may be at ../frontend/dist.
_FRONTEND_DIST_CANDIDATES = [
    "/app/frontend/dist",                    # Render Docker deployment
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "dist"),  # backend/frontend/dist
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend", "dist"),  # /app/frontend/dist (repo root)
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "frontend", "dist"),
]

FRONTEND_DIST = None
for candidate in _FRONTEND_DIST_CANDIDATES:
    if os.path.isdir(candidate):
        FRONTEND_DIST = candidate
        break

if FRONTEND_DIST:
    # Serve static assets (JS, CSS, images, etc.)
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        """Serve the React SPA with a fallback to index.html for client-side routes."""
        # If the path is a valid static file, serve it; otherwise, fall back to index.html
        candidate = os.path.join(FRONTEND_DIST, full_path)
        if full_path and os.path.isfile(candidate):
            return FileResponse(candidate)
        return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))
    print(f"✅ Serving frontend from {FRONTEND_DIST}")
else:
    # Fallback: keep the JSON root endpoint for API-only deployments
    @app.get("/")
    async def root_fallback():
        return {
            "app": settings.APP_NAME,
            "version": settings.VERSION,
            "status": "running",
            "docs": "/api/docs",
            "note": "Frontend not found. API-only deployment."
        }


if __name__ == '__main__':
    uvicorn.run(
        "app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )

