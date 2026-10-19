from fastapi import APIRouter
from app.api.health import router as health_router
from app.api.services import router as services_router
from app.api.dependencies import router as dependencies_router
from app.api.graph import router as graph_router
from app.api.metrics import router as metrics_router
from app.api.anomaly_routes import router as anomaly_router
from app.api.metrics_routes import router as metrics_stream_router
from app.api.alert_routes import router as alert_router

api_router = APIRouter(prefix="/api")
api_router.include_router(health_router)
api_router.include_router(services_router)
api_router.include_router(dependencies_router)
api_router.include_router(graph_router)
api_router.include_router(metrics_router)

# Module 2 routes
api_router.include_router(anomaly_router)
api_router.include_router(metrics_stream_router)
api_router.include_router(alert_router)

# Module 3 routes
from app.api.cascade_routes import router as cascade_router
api_router.include_router(cascade_router)

# Module 4 routes
from app.api.rca_routes import router as rca_router
api_router.include_router(rca_router)

# Module 5 routes
from app.api.agent_routes import router as agent_router
api_router.include_router(agent_router)

# Module 6 routes
from app.api.simulation_routes import router as simulation_router
api_router.include_router(simulation_router)


