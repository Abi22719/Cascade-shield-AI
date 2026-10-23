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

# Module 7 routes
from app.api.recovery_routes import router as recovery_router
api_router.include_router(recovery_router)

# Module 8 routes
from app.api.validation_routes import router as validation_router
api_router.include_router(validation_router)

# Module 9 routes
from app.api.benchmark_routes import router as benchmark_router
api_router.include_router(benchmark_router)

# Module 10 routes
from app.api.dashboard_routes import router as dashboard_router
from app.api.search_routes import router as search_router
from app.api.notification_routes import router as notification_router
from app.api.report_routes import router as report_router
from app.api.workflow_routes import router as workflow_router

api_router.include_router(dashboard_router)
api_router.include_router(search_router)
api_router.include_router(notification_router)
api_router.include_router(report_router)
api_router.include_router(workflow_router)

# Enterprise Portals 1-8 routes
from app.api.admin_routes import router as admin_router
from app.api.incident_routes import router as incident_router
from app.api.copilot_routes import router as copilot_router
from app.api.developer_routes import router as developer_router
from app.api.security_routes import router as security_router
from app.api.knowledge_routes import router as knowledge_router

api_router.include_router(admin_router)
api_router.include_router(incident_router)
api_router.include_router(copilot_router)
api_router.include_router(developer_router)
api_router.include_router(security_router)
api_router.include_router(knowledge_router)


