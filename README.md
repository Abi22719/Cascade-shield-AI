# CascadeShield AI – Module 1: Cloud Digital Twin & Dependency Mapping

**CascadeShield AI** is an AI-powered cloud resilience digital twin and intelligent failure prevention platform.

This repository implements **Module 1: Cloud Digital Twin and Dependency Mapping**, providing the foundational virtual infrastructure model, interactive dependency graph, simulated telemetry engine, rule-based health evaluator, and downstream blast radius analyzer required by Modules 2–10.

---

## 1. System Architecture

```mermaid
flowchart TD
    subgraph Client["Frontend Client (React.js + Cytoscape.js)"]
        UI["Modern Dark Operations Dashboard"]
        Cy["Cytoscape.js Canvas (Dagre / Cose / Breadthfirst)"]
        Drawer["Service Inspector & Blast Radius Drawer"]
        Sim["Interactive Telemetry Simulator & Presets"]
    end

    subgraph API["FastAPI Modular Backend (Python 3.14+)"]
        Router["REST API Router (/api)"]
        HealthRules["Rule-Based Health Evaluator"]
        GraphEngine["NetworkX DiGraph Engine"]
    end

    subgraph Storage["Persistent Storage"]
        DB[("SQLite Database: cascadeshield.db")]
        Tables["Services Table & Dependencies Table (Foreign Keys + Cascade)"]
    end

    UI -->|REST / JSON| Router
    Cy -->|Tap Node / Edge| Drawer
    Drawer -->|Simulate Sliders| Sim
    Sim -->|PUT /api/services/{id}| Router
    Router --> HealthRules
    Router --> GraphEngine
    Router --> DB
    DB --> Tables
    GraphEngine -->|Cycle Detection & Impact Analysis| Router
    Router -->|Nodes, Edges, Health, Cycles| Cy
```

---

## 2. Cloud Infrastructure Model

Module 1 initializes a virtual representation of standard multi-tier cloud infrastructure consisting of **9 default services** connected through directed dependencies:

| Service ID | Service Name | Service Type | Role & Description |
| :--- | :--- | :--- | :--- |
| `srv-gateway` | **API Gateway** | `gateway` | Edge ingress routing layer, rate-limiting, SSL termination |
| `srv-auth` | **Authentication Service** | `security` | Token verification, OAuth2, RBAC identity management |
| `srv-user` | **User Service** | `compute` | User accounts, profiles, preferences persistence |
| `srv-product` | **Product Service** | `compute` | Product catalog, pricing, inventory metadata |
| `srv-order` | **Order Service** | `compute` | Checkout workflows, order orchestration, transaction state |
| `srv-payment` | **Payment Service** | `compute` | Third-party payment gateway, ledger, fraud checks |
| `srv-notify` | **Notification Service** | `messaging` | Async customer notifications (email, SMS, webhooks) |
| `srv-database` | **Database Service** | `database` | Primary ACID relational database cluster |
| `srv-cache` | **Cache Service** | `cache` | Redis in-memory high-throughput cache cluster |

### Default Dependency Flow
- `API Gateway` &rarr; `Authentication Service` &rarr; `User Service`
- `API Gateway` &rarr; `Product Service` &rarr; `Database Service`
- `API Gateway` &rarr; `Order Service` &rarr; `Payment Service`
- `Order Service` &rarr; `Database Service`
- `Order Service` &rarr; `Notification Service`
- `Product Service` &rarr; `Cache Service`

---

## 3. Key Capabilities

### 3.1. Interactive Cytoscape.js Dependency Graph
- **Dynamic Layouts**: Hierarchical Left-to-Right (`dagre-lr`), Top-to-Bottom (`dagre-tb`), Breadth-first (`breadthfirst`), Force-Directed (`cose`), and Circular.
- **Node Health Badging**: Distinct color-coded status rings:
  - 🟢 **HEALTHY** (`#10b981`)
  - 🟡 **WARNING** (`#f59e0b`)
  - 🔴 **CRITICAL** (`#ef4444`)
- **Edge Protocol Distinction**: Solid arrows for Synchronous HTTP, dashed for Asynchronous Queues, database read/write connections, and cache lookups.
- **Controls**: Zoom in/out, fit to screen, center viewport, re-run layout, and filter toolbar.
- **Cycle Detection**: Real-time detection of circular dependencies with warning banners, highlighting cycle paths.

### 3.2. Rule-Based Health Evaluator
Health status is dynamically calculated from simulated telemetry using explicit, transparent rules rather than random mutations:
- **CRITICAL** if:
  - `error_rate >= 10.0%` OR `latency_ms >= 1000.0ms` OR `cpu_usage >= 90.0%` OR `memory_usage >= 92.0%`
- **WARNING** if:
  - `error_rate >= 2.0%` OR `latency_ms >= 400.0ms` OR `cpu_usage >= 75.0%` OR `memory_usage >= 80.0%`
- **HEALTHY**: All operating metrics within baseline thresholds.

### 3.3. Downstream Blast Radius & Impact Mapping
Calculates the exact set of downstream services reachable from a chosen root service using NetworkX directed graph traversal (`nx.descendants` and `nx.shortest_path`).
- Identifies **Direct Dependents (Hop 1)** vs **Transitive Dependents (Hop 2+)**.
- Highlights the entire blast radius path on the Cytoscape graph canvas.
- Prepared for Module 3 cascading failure simulation without premature failure probability claims.

### 3.4. Simulated Telemetry Injection & Scenarios
Users can simulate conditions using real-time sliders or quick scenario presets:
- **Normal Baseline**
- **Traffic Surge**
- **Critical Outage**
- **Latency Spike**

All metrics are clearly designated with a `[Simulated Telemetry]` badge.

---

## 4. Backend REST API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Service liveness and database connection status |
| `GET` | `/api/services` | List all services (supports `service_type`, `health_status`, `search` query filters) |
| `GET` | `/api/services/{service_id}` | Retrieve service details, incoming callers, outgoing dependencies, and health rationale |
| `POST` | `/api/services` | Register a new cloud service with simulated telemetry |
| `PUT` | `/api/services/{service_id}` | Update service metadata or simulated metrics (triggers health recalculation) |
| `DELETE` | `/api/services/{service_id}` | Delete a service (cascades deletion to connected dependencies) |
| `GET` | `/api/dependencies` | List all dependencies (supports `source_id`, `target_id` filters) |
| `POST` | `/api/dependencies` | Create directed dependency (validates existence, blocks self/duplicates, flags cycles) |
| `DELETE` | `/api/dependencies/{dependency_id}` | Remove a directed dependency edge |
| `GET` | `/api/graph` | Cytoscape-formatted graph payload with node telemetry and cycle detection summary |
| `GET` | `/api/graph/impact/{service_id}` | Calculate downstream reachable services and shortest impact paths |
| `POST` | `/api/graph/reset` | Restore baseline 9-service topology and default dependencies |
| `GET` | `/api/metrics/summary` | Aggregate cluster metrics (total, healthy, warning, critical, health score %, avg latency) |

---

## 5. Integration Interfaces for Modules 2–10

Module 1 establishes the canonical data contracts and models for upcoming modules:
- **Module 2 (AI Anomaly Detection)**: Integrates with `app/models/service.py` telemetry fields and `/api/metrics/summary` to detect metric outliers.
- **Module 3 (Cascading Failure Prediction)**: Consumes the NetworkX graph and `/api/graph/impact/{service_id}` to calculate failure propagation probabilities across dependency tiers.
- **Module 4 (Root Cause Analysis)**: Uses the directed dependency graph and incoming caller relationships to trace upstream triggers.
- **Module 5–8 (Diagnostics, What-If, Recovery, Fault Injection)**: Leverages the simulation endpoints (`PUT /api/services/{id}`) and graph mutations to execute safe failure injection experiments.
- **Module 9–10 (Benchmarking & Resilience Command Dashboard)**: Reads aggregate metrics and health scores from `/api/metrics/summary` and `/api/graph`.

---

## 6. Installation & Execution Guide

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 6.1. Backend Setup & Run

1. Navigate to the backend directory:
   ```powershell
   cd backend
   ```

2. Install Python dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

3. Run automated tests (pytest):
   ```powershell
   python -m pytest -v
   ```
   *(All 24 unit and integration tests will execute and verify database seeding, CRUD, cycles, impact analysis, and persistence).*

4. Start the FastAPI server:
   ```powershell
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
   - API is accessible at: `http://127.0.0.1:8000`
   - Interactive Swagger API Documentation: `http://127.0.0.1:8000/docs`

---

### 6.2. Frontend Setup & Run

1. Navigate to the frontend directory:
   ```powershell
   cd frontend
   ```

2. Install npm dependencies:
   ```powershell
   npm install
   ```

3. Start the Vite React development server:
   ```powershell
   npm run dev
   ```
   - Frontend is accessible at: `http://localhost:5173`

---

## 7. Assumptions and Limitations

1. **Simulated Telemetry**: Telemetry metrics (CPU, Memory, Latency, Error Rate, Request Volume) are synthetic and simulated for modeling and testing resilience scenarios. No live cloud credentials (AWS/GCP/Azure) are required for Module 1.
2. **Blast Radius Traversal**: The downstream impact endpoint calculates topological reachability (services reachable via directed edges). Actual failure probability modeling is reserved for Module 3.
3. **Circular Dependencies**: NetworkX detects circular loops when dependencies are created. Rather than outright rejecting intentional circular patterns in complex microservices, the system creates the dependency while surfacing an explicit warning and highlighting the cycle in the UI.
