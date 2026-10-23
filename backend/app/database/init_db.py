from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.service import ServiceModel
from app.models.dependency import DependencyModel
from app.models.security_models import UserModel, AuditLogModel
from app.models.knowledge_models import KnowledgeArticleModel
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

    now = datetime.now(timezone.utc)

    existing_services_count = db.query(ServiceModel).count()
    if existing_services_count == 0 or force_reset:
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

    # Seed initial enterprise users if empty
    if db.query(UserModel).count() == 0:
        default_users = [
            UserModel(
                id="usr-admin-01",
                username="admin@cascadeshield.ai",
                full_name="Sarah Connor (Principal SRE)",
                email="admin@cascadeshield.ai",
                role="Administrator",
                is_active=True,
                last_login=now
            ),
            UserModel(
                id="usr-op-01",
                username="operator@cascadeshield.ai",
                full_name="Alex Chen (Cloud Operator)",
                email="operator@cascadeshield.ai",
                role="Cloud Operator",
                is_active=True,
                last_login=now
            ),
            UserModel(
                id="usr-resp-01",
                username="responder@cascadeshield.ai",
                full_name="Maya Lin (Incident Commander)",
                email="responder@cascadeshield.ai",
                role="Incident Responder",
                is_active=True,
                last_login=now
            ),
            UserModel(
                id="usr-analyst-01",
                username="analyst@cascadeshield.ai",
                full_name="Jordan Reed (Reliability Analyst)",
                email="analyst@cascadeshield.ai",
                role="Analyst",
                is_active=True,
                last_login=now
            ),
            UserModel(
                id="usr-dev-01",
                username="developer@cascadeshield.ai",
                full_name="David Patel (Platform Engineer)",
                email="developer@cascadeshield.ai",
                role="Developer",
                is_active=True,
                last_login=now
            ),
            UserModel(
                id="usr-viewer-01",
                username="viewer@cascadeshield.ai",
                full_name="Auditor Executive (Read-Only)",
                email="viewer@cascadeshield.ai",
                role="Read-Only Viewer",
                is_active=True,
                last_login=now
            )
        ]
        db.add_all(default_users)
        db.commit()

    # Seed initial audit logs if empty
    if db.query(AuditLogModel).count() == 0:
        default_audits = [
            AuditLogModel(
                id="audit-001",
                actor_id="usr-admin-01",
                actor_name="Sarah Connor",
                actor_role="Administrator",
                action="TOPOLOGY_INIT",
                resource_type="digital_twin",
                resource_id="srv-topology",
                status="SUCCESS",
                details_json='{"action": "Initial baseline digital twin configuration established with 9 services and 11 dependencies."}',
                timestamp=now
            ),
            AuditLogModel(
                id="audit-002",
                actor_id="usr-resp-01",
                actor_name="Maya Lin",
                actor_role="Incident Responder",
                action="RCA_ANALYSIS",
                resource_type="rca_incident",
                resource_id="inc-payment-cascade-01",
                status="SUCCESS",
                details_json='{"root_cause": "srv-payment", "confidence": 0.96, "blast_radius": 3}',
                timestamp=now
            ),
            AuditLogModel(
                id="audit-003",
                actor_id="usr-op-01",
                actor_name="Alex Chen",
                actor_role="Cloud Operator",
                action="SIMULATION_EXECUTE",
                resource_type="simulation_run",
                resource_id="sim-run-payment-outage",
                status="SUCCESS",
                details_json='{"scenario": "service_unavailable", "target": "srv-payment", "duration_steps": 10}',
                timestamp=now
            ),
            AuditLogModel(
                id="audit-004",
                actor_id="usr-admin-01",
                actor_name="Sarah Connor",
                actor_role="Administrator",
                action="RECOVERY_VERIFY",
                resource_type="validation_run",
                resource_id="val-run-circuit-breaker",
                status="SUCCESS",
                details_json='{"outcome": "VERIFIED_SUCCESS", "pillars_passed": 5, "sla_breach": false}',
                timestamp=now
            )
        ]
        db.add_all(default_audits)
        db.commit()

    # Seed initial knowledge base articles if empty
    if db.query(KnowledgeArticleModel).count() == 0:
        default_articles = [
            KnowledgeArticleModel(
                id="kb-sop-001",
                title="SOP-01: Payment Gateway Circuit-Breaker Isolation Procedure",
                category="sop",
                summary="Standard operating procedure for isolating degraded payment gateways without user-facing 500 errors.",
                content="""# SOP-01: Payment Gateway Circuit-Breaker Isolation

## 1. Overview
When `srv-payment` experiences latency > 1500ms or error rate > 5%, downstream cascade propagation immediately degrades `srv-order` and `srv-gateway`. This SOP governs the execution of automated circuit isolation.

## 2. Trigger Criteria
- Isolation Forest anomaly alert severity = `CRITICAL`
- Consecutive downstream HTTP 502/504 errors on `/api/v1/checkout` > 50 req/sec.

## 3. Execution Steps
1. Execute virtual sandbox simulation of recovery plan `RP-PAYMENT-FAILOVER`.
2. Verify preconditions: `traffic_drained = true`, `secondary_provider_available = true`.
3. Enable circuit breaker: Route 100% of checkout payload to secondary Stripe token backup pool.
4. Run 5-Pillar Validation to ensure P99 latency returns < 150ms.
5. If recovery fails, execute automated rollback sequence to restore baseline routing.

## 4. Verification Checkpoints
- Service health status returns to `HEALTHY`.
- Latency P99 drops below 120ms.
- Zero cyclic routing dependencies detected.
""",
                service_id="srv-payment",
                tags_json='["payment", "circuit-breaker", "sop", "failover", "checkout"]',
                author="Sarah Connor (Principal SRE)"
            ),
            KnowledgeArticleModel(
                id="kb-playbook-002",
                title="Playbook: PostgreSQL Database Connection Pool Exhaustion Mitigation",
                category="playbook",
                summary="Resolution steps for query queue saturation, connection pool leaks, and multi-service downstream cascade.",
                content="""# Playbook: PostgreSQL Connection Pool Exhaustion

## 1. Symptoms
- `srv-database` CPU utilization > 92%
- Active connections = `max_connections` (250/250)
- Downstream services (`srv-user`, `srv-order`, `srv-product`, `srv-auth`) report database socket timeout.

## 2. Blast Radius Analysis
Inverted reverse propagation shows `srv-database` has in-degree of 4, creating an immediate widespread cascade across 80% of customer endpoints.

## 3. Remediation Sequence
1. Identify and terminate long-running idle transactions: `SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle in transaction'`.
2. Enable read-replica load offloading for `srv-product` and `srv-user` queries.
3. Reload PgBouncer connection pooler with dynamic client queue throttling.
4. Scale connection allocation pool by 50% in the digital twin infrastructure model.
""",
                service_id="srv-database",
                tags_json='["database", "postgres", "connection-pool", "saturation", "playbook"]',
                author="David Patel (Platform Engineer)"
            ),
            KnowledgeArticleModel(
                id="kb-troubleshoot-003",
                title="Troubleshooting Guide: Redis Cache Stampede & Eviction Waves",
                category="troubleshooting",
                summary="Diagnostics and prevention for cache stampedes causing sudden database CPU spikes.",
                content="""# Troubleshooting Guide: Redis Cache Stampede

## 1. Problem Description
A cache stampede occurs when high-frequency cache keys expire simultaneously, deflecting high-concurrency requests directly to the database.

## 2. Root Cause Attribution
- Cache hit ratio drops abruptly from 95% to < 15%.
- Database CPU spikes by 400% within 15 seconds.
- Memory fragmentation ratio on Redis cluster > 1.8.

## 3. Resolution Steps
1. Apply probabilistic early expiration (XFetch algorithm) to high-volume catalog keys.
2. Inject jitter (+/- 10% random offset) into key TTL definitions.
3. Pre-warm Redis cache partition before releasing traffic restrictions.
""",
                service_id="srv-cache",
                tags_json='["cache", "redis", "stampede", "eviction", "troubleshooting"]',
                author="Alex Chen (Cloud Operator)"
            ),
            KnowledgeArticleModel(
                id="kb-postmortem-004",
                title="Post-Mortem: Incident INC-2026-10-PAYMENT Cascading Checkout Outage",
                category="postmortem",
                summary="Audited post-mortem analysis of cascading failure triggered by third-party payment provider latency.",
                content="""# Post-Mortem: INC-2026-10-PAYMENT

## Executive Summary
On October 21, 2026, an external payment provider degraded, increasing latency on `srv-payment` to 4200ms. Synchronous HTTP coupling between `srv-order` and `srv-payment` led to worker thread exhaustion on API Gateway. CascadeShield AI detected the anomaly within 1.2s, identified `srv-payment` as root cause with 96% confidence, and validated circuit-breaker recovery.

## Timeline
- **T0**: Latency spike on `srv-payment` (4200ms).
- **T+1.2s**: Module 2 detects Isolation Forest breach and raises CRITICAL alert.
- **T+2.5s**: Module 3 calculates reverse blast radius: `srv-payment` -> `srv-order` -> `srv-gateway`.
- **T+4.1s**: Module 4 RCA isolates `srv-payment` with top candidate score (96/100).
- **T+6.0s**: Module 7 generates 4 candidate recovery strategies; Balanced strategy selected.
- **T+8.2s**: Module 8 verifies recovery across all 5 resilience pillars.
- **T+10.0s**: SLA compliance restored.

## Action Items
1. Convert synchronous order-to-payment calls to asynchronous queue pattern.
2. Lower circuit breaker trip threshold from 2000ms to 800ms.
""",
                service_id="srv-payment",
                tags_json='["postmortem", "incident", "lessons-learned", "resilience", "audit"]',
                author="Maya Lin (Incident Commander)"
            )
        ]
        db.add_all(default_articles)
        db.commit()
