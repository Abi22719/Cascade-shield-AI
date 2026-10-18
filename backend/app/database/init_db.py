from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.service import ServiceModel
from app.models.dependency import DependencyModel
from app.services.health_evaluator import evaluate_service_health

DEFAULT_SERVICES = [
    {
        "id": "srv-gateway",
        "name": "API Gateway",
        "service_type": "gateway",
        "description": "Edge routing layer, SSL termination, and rate limiting for incoming client requests.",
        "cpu_usage": 24.5,
        "memory_usage": 38.0,
        "latency_ms": 18.2,
        "error_rate": 0.05,
        "request_volume": 4200,
    },
    {
        "id": "srv-auth",
        "name": "Authentication Service",
        "service_type": "security",
        "description": "JWT issuance, OAuth2 token verification, and RBAC authorization verification.",
        "cpu_usage": 32.0,
        "memory_usage": 42.5,
        "latency_ms": 32.4,
        "error_rate": 0.12,
        "request_volume": 2800,
    },
    {
        "id": "srv-user",
        "name": "User Service",
        "service_type": "compute",
        "description": "Manages user account profiles, preferences, and identity state.",
        "cpu_usage": 28.4,
        "memory_usage": 45.0,
        "latency_ms": 42.0,
        "error_rate": 0.15,
        "request_volume": 1950,
    },
    {
        "id": "srv-product",
        "name": "Product Service",
        "service_type": "compute",
        "description": "Handles product catalog querying, inventory metadata, and pricing lookups.",
        "cpu_usage": 35.8,
        "memory_usage": 52.3,
        "latency_ms": 55.6,
        "error_rate": 0.20,
        "request_volume": 2400,
    },
    {
        "id": "srv-order",
        "name": "Order Service",
        "service_type": "compute",
        "description": "Coordinates cart checkout workflows, order placement, and transaction state.",
        "cpu_usage": 41.2,
        "memory_usage": 58.7,
        "latency_ms": 78.4,
        "error_rate": 0.35,
        "request_volume": 1200,
    },
    {
        "id": "srv-payment",
        "name": "Payment Service",
        "service_type": "compute",
        "description": "Handles third-party payment gateway integration, billing ledger, and fraud checks.",
        "cpu_usage": 29.5,
        "memory_usage": 41.0,
        "latency_ms": 115.0,
        "error_rate": 0.45,
        "request_volume": 850,
    },
    {
        "id": "srv-notify",
        "name": "Notification Service",
        "service_type": "messaging",
        "description": "Dispatches asynchronous email, SMS, and webhook alerts to customers and systems.",
        "cpu_usage": 19.0,
        "memory_usage": 31.5,
        "latency_ms": 25.0,
        "error_rate": 0.08,
        "request_volume": 650,
    },
    {
        "id": "srv-database",
        "name": "Database Service",
        "service_type": "database",
        "description": "Primary relational database cluster storing relational domain entities and ACID transactions.",
        "cpu_usage": 48.6,
        "memory_usage": 64.2,
        "latency_ms": 14.5,
        "error_rate": 0.02,
        "request_volume": 4900,
    },
    {
        "id": "srv-cache",
        "name": "Cache Service",
        "service_type": "cache",
        "description": "High-throughput in-memory Redis cluster for session caching and read-heavy catalog items.",
        "cpu_usage": 15.2,
        "memory_usage": 51.0,
        "latency_ms": 2.8,
        "error_rate": 0.01,
        "request_volume": 5600,
    },
]

DEFAULT_DEPENDENCIES = [
    {
        "id": "dep-gateway-auth",
        "source_service_id": "srv-gateway",
        "target_service_id": "srv-auth",
        "dependency_type": "sync_http",
        "description": "API Gateway routes client credentials and auth token validation to Authentication Service."
    },
    {
        "id": "dep-auth-user",
        "source_service_id": "srv-auth",
        "target_service_id": "srv-user",
        "dependency_type": "sync_http",
        "description": "Authentication Service queries User Service to verify account standing and identity credentials."
    },
    {
        "id": "dep-gateway-product",
        "source_service_id": "srv-gateway",
        "target_service_id": "srv-product",
        "dependency_type": "sync_http",
        "description": "API Gateway forwards catalog search and browse requests to Product Service."
    },
    {
        "id": "dep-product-database",
        "source_service_id": "srv-product",
        "target_service_id": "srv-database",
        "dependency_type": "database_read_write",
        "description": "Product Service queries primary relational database for catalog persistence."
    },
    {
        "id": "dep-product-cache",
        "source_service_id": "srv-product",
        "target_service_id": "srv-cache",
        "dependency_type": "cache_lookup",
        "description": "Product Service checks Redis cache before querying DB for hot catalog listings."
    },
    {
        "id": "dep-gateway-order",
        "source_service_id": "srv-gateway",
        "target_service_id": "srv-order",
        "dependency_type": "sync_http",
        "description": "API Gateway proxies checkout and order submission traffic to Order Service."
    },
    {
        "id": "dep-order-payment",
        "source_service_id": "srv-order",
        "target_service_id": "srv-payment",
        "dependency_type": "sync_http",
        "description": "Order Service initiates synchronous payment processing with Payment Service during checkout."
    },
    {
        "id": "dep-order-database",
        "source_service_id": "srv-order",
        "target_service_id": "srv-database",
        "dependency_type": "database_read_write",
        "description": "Order Service commits finalized order records and receipts to primary database."
    },
    {
        "id": "dep-order-notify",
        "source_service_id": "srv-order",
        "target_service_id": "srv-notify",
        "dependency_type": "async_message",
        "description": "Order Service triggers async order confirmation notifications to customer notification worker."
    },
]

def init_db(db: Session, force_reset: bool = False):
    """
    Initializes default services and dependencies if the tables are empty,
    or resets them when force_reset is True.
    """
    if force_reset:
        db.query(DependencyModel).delete()
        db.query(ServiceModel).delete()
        db.commit()

    existing_services_count = db.query(ServiceModel).count()
    if existing_services_count > 0 and not force_reset:
        # Already initialized, do not duplicate
        return

    now = datetime.now(timezone.utc)

    # Insert default services
    for s_data in DEFAULT_SERVICES:
        status, _ = evaluate_service_health(
            cpu_usage=s_data["cpu_usage"],
            memory_usage=s_data["memory_usage"],
            latency_ms=s_data["latency_ms"],
            error_rate=s_data["error_rate"],
        )
        service = ServiceModel(
            id=s_data["id"],
            name=s_data["name"],
            service_type=s_data["service_type"],
            description=s_data["description"],
            health_status=status,
            cpu_usage=s_data["cpu_usage"],
            memory_usage=s_data["memory_usage"],
            latency_ms=s_data["latency_ms"],
            error_rate=s_data["error_rate"],
            request_volume=s_data["request_volume"],
            updated_at=now
        )
        db.add(service)

    db.commit()

    # Insert default dependencies
    for d_data in DEFAULT_DEPENDENCIES:
        dep = DependencyModel(
            id=d_data["id"],
            source_service_id=d_data["source_service_id"],
            target_service_id=d_data["target_service_id"],
            dependency_type=d_data["dependency_type"],
            description=d_data["description"]
        )
        db.add(dep)

    db.commit()
