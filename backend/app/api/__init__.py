from fastapi import APIRouter
from app.api.health import router as health_router
from app.api.services import router as services_router
from app.api.dependencies import router as dependencies_router
from app.api.graph import router as graph_router
from app.api.metrics import router as metrics_router

api_router = APIRouter(prefix="/api")
api_router.include_router(health_router)
api_router.include_router(services_router)
api_router.include_router(dependencies_router)
api_router.include_router(graph_router)
api_router.include_router(metrics_router)
