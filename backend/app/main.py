import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.database import engine, Base, SessionLocal
from app.database.init_db import init_db
import app.models  # Ensures all models (ServiceModel, DependencyModel, AlertModel) are registered
from app.api import api_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("cascadeshield")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables
    logger.info("Initializing database schema...")
    Base.metadata.create_all(bind=engine)
    
    # Seed default sample cloud infrastructure if database is empty
    db = SessionLocal()
    try:
        init_db(db, force_reset=False)
        logger.info("Database initialized successfully with default cloud twin baseline.")
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
    finally:
        db.close()

    yield
    logger.info("CascadeShield AI digital twin engine shutting down.")

app = FastAPI(
    title="CascadeShield AI - Cloud Resilience Digital Twin & Intelligent Agent",
    description="Modules 1, 2, 3 & 4: Digital Twin, Anomaly Detection, Cascade Prediction & Root Cause Analysis",
    version="4.0.0",
    lifespan=lifespan
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get("/")
def root():
    return {
        "project": "CascadeShield AI",
        "modules": [
            "Module 1: Cloud Digital Twin and Dependency Mapping",
            "Module 2: AI-Based Anomaly Detection and Early Warning",
            "Module 3: Cascading Failure Prediction Engine",
            "Module 4: Evidence-Grounded Root Cause Analysis"
        ],
        "status": "operational",
        "api_docs": "/docs",
        "endpoints": {
            "health": "/api/health",
            "services": "/api/services",
            "dependencies": "/api/dependencies",
            "graph": "/api/graph",
            "anomalies_summary": "/api/anomalies/summary",
            "anomalies_detect": "/api/anomalies/detect",
            "anomalies_evaluation": "/api/anomalies/evaluation",
            "anomalies_thresholds": "/api/anomalies/thresholds"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
