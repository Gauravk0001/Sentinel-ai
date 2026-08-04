# SentinelAI 🛡️

## AI-Powered Insider Data Exfiltration Detection Platform

SentinelAI is a production-grade enterprise cybersecurity platform that detects insider data exfiltration attempts without inspecting the content of user files. It uses behavioral analytics, metadata analysis, and machine learning to identify suspicious activities while preserving user privacy.

## Features

- **Zero-Content Inspection** - Never reads file contents, only analyzes metadata
- **Real-Time Monitoring** - Track employee activities across multiple vectors
- **AI-Powered Detection** - Isolation Forest & XGBoost for anomaly detection
- **Explainable AI** - SHAP-based explanations for every alert
- **Enterprise Dashboard** - Modern, responsive UI with dark theme
- **Role-Based Access** - Admin, Security Analyst, Compliance Officer
- **Automated Response** - Incident management and alerting
- **Comprehensive Reporting** - PDF & CSV exports

## Tech Stack

### Frontend
- React 19 + TypeScript
- Vite + TailwindCSS
- Shadcn UI + Framer Motion
- Recharts + React Query

### Backend
- Python FastAPI
- WebSocket for real-time updates
- JWT Authentication
- PostgreSQL + Redis

### AI Engine
- Scikit-learn (Isolation Forest)
- XGBoost
- SHAP Explainability
- Feature Engineering Pipeline

## Quick Start

```bash
# Clone the repository
git clone https://github.com/yourorg/sentinelai.git
cd sentinelai

# Start with Docker
docker-compose up -d

# Or manual setup
cd backend && pip install -r requirements.txt
cd frontend && npm install && npm run dev
```

## Architecture

```
sentinelai/
├── frontend/          # React SPA
├── backend/           # FastAPI server
├── ai_engine/         # ML models & pipelines
├── dataset/           # Synthetic data generator
├── docker/            # Docker configurations
└── docs/              # Documentation
```

## License

MIT

