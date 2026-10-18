# CascadeShield AI – AI-Powered Cloud Resilience Digital Twin & Intelligent Failure Prevention Agent

CascadeShield AI is an intelligent cloud resilience platform providing virtual digital twin modeling, dependency analysis, AI-based anomaly detection, early warning alerts, and automated failure prevention.

---

## 1. System Architecture

```mermaid
flowchart TD
    subgraph UI["Frontend (React.js + Cytoscape.js + Recharts)"]
        Nav["Navbar (Module 1 / Module 2 Switcher)"]
        Twin["Module 1: Digital Twin & Dependency Graph"]
        Anomaly["Module 2: Anomaly Detection Dashboard"]
        Trend["Time-Series Telemetry Charts with Threshold Reference Lines"]
        Table["Anomaly Incident Table & Acknowledgment"]
        Eval["Benchmark Evaluation Comparison (Precision, Recall, F1)"]
    end

    subgraph Backend["FastAPI Modular Backend (Python 3.10+)"]
        API["REST Router (/api)"]
        GraphEngine["NetworkX DiGraph Engine (Module 1)"]
        ThresholdEngine["Configurable Threshold Detector (Module 2)"]
        MLEngine["Scikit-Learn Isolation Forest Engine (Module 2)"]
        AlertEngine["Alert Classifier & Deduplication Service"]
        EvaluationEngine["Benchmark Ground-Truth Evaluation Service"]
    end

    subgraph Storage["SQLite Persistent Database"]
        DB[("cascadeshield.db")]
        T1["Services Table (9 Default Services)"]
        T2["Dependencies Table (Directed Flow)"]
        T3["Alerts Table (Indexed, Deduplicated & Persistent)"]
    end

    Nav --> Twin
    Nav --> Anomaly
    Anomaly --> Trend
    Anomaly --> Table
    Anomaly --> Eval

    Twin <-->|REST| API
    Anomaly <-->|REST| API

    API --> GraphEngine
    API --> ThresholdEngine
    API --> MLEngine
    API --> AlertEngine
    API --> EvaluationEngine

    API <--> DB
    DB --> T1
    DB --> T2
    DB --> T3
```

---

## 2. Modules Overview

### 2.1. Module 1: Cloud Digital Twin & Dependency Mapping
- **9 Canonical Services**: API Gateway, Authentication, User, Product, Order, Payment, Notification, Database, and Cache.
- **Cytoscape.js Dependency Graph**: Hierarchical Dagre (LR/TB), Breadthfirst, and Cose layouts.
- **NetworkX DiGraph**: Real-time cycle detection, downstream blast radius traversal, and path routing.
- **Simulated Telemetry**: CPU, Memory, Latency, Error Rate, and Request Throughput.

### 2.2. Module 2: AI-Based Anomaly Detection and Early Warning
- **Threshold Rule Engine**: Configurable warning and critical operating limits for CPU, Memory, Latency, and Error Rate.
- **Scikit-Learn Isolation Forest**: Multivariate statistical outlier detection using high-dimensional feature spaces `[cpu, memory, latency, error_rate, request_volume]`.
- **Tri-Tier Severity Classification**: `Normal`, `Warning`, and `Critical` alerts with evidence summaries.
- **Deduplication & SQLite Persistence**: Prevents alert flooding within active incident windows; stores alerts in SQLite.
- **Interactive Metric Trends**: Recharts time-series visualization with warning/critical threshold lines and service selection.
- **Benchmark Evaluation**: Evaluates True Positives, False Positives, True Negatives, False Negatives, Precision, Recall, F1-Score, and False Positive Rate across 200 labeled observations.

---

## 3. REST API Reference

### Module 1 Endpoints
- `GET /api/health`: System health and SQLite connection status
- `GET /api/services`: List services with filtering by type, status, and search
- `GET /api/services/{id}`: Service detail with callers and downstream dependents
- `POST /api/services`: Register new cloud service
- `PUT /api/services/{id}`: Update service metadata and telemetry
- `DELETE /api/services/{id}`: Delete service (cascades dependencies)
- `GET /api/dependencies`: List dependencies
- `POST /api/dependencies`: Connect two services (cycle detection warning)
- `DELETE /api/dependencies/{id}`: Remove dependency
- `GET /api/graph`: Cytoscape-formatted graph payload
- `GET /api/graph/impact/{id}`: Downstream blast radius analysis
- `POST /api/graph/reset`: Reset to baseline 9-service topology
- `GET /api/metrics/summary`: Aggregate cluster health metrics

### Module 2 Endpoints
- `GET /api/anomalies/health`: Anomaly subsystem health
- `GET /api/anomalies/summary`: Total alerts, critical, warning, anomalous observations, and affected services
- `GET /api/anomalies`: Query alerts with pagination and filters (`service_id`, `severity`, `detection_method`, `acknowledged`)
- `GET /api/anomalies/{alert_id}`: Alert evidence details
- `POST /api/anomalies/detect`: Execute anomaly detection scan (`combined`, `threshold`, `isolation_forest`)
- `GET /api/anomalies/metrics/{service_id}`: Time-series telemetry points for chart visualization
- `GET /api/anomalies/thresholds`: Current threshold configuration
- `PUT /api/anomalies/thresholds`: Update warning and critical thresholds
- `GET /api/anomalies/evaluation`: Benchmark comparative metrics (Precision, Recall, F1)
- `POST /api/anomalies/{alert_id}/acknowledge`: Acknowledge an alert

---

## 4. Benchmark Evaluation Results

Evaluated across **200 labeled observations** (160 normal, 40 anomalous):

| Metric | 1. Threshold Rules | 2. Isolation Forest (ML) | 3. Combined Alerting |
| :--- | :---: | :---: | :---: |
| **Precision** | ~95.2% | ~85.4% | ~93.0% |
| **Recall** | ~50.0% | ~87.5% | **100.0%** |
| **F1-Score** | 0.656 | 0.864 | **0.964** |
| **Accuracy** | 90.0% | 94.5% | **98.5%** |
| **False Positive Rate** | 0.6% | 3.8% | 1.9% |

*Key finding: Threshold rules catch single-metric spikes with near-zero false alarms; Isolation Forest detects subtle multivariate anomalies; the combined approach maximizes recall and prevents blind spots.*

---

## 5. Installation & Execution Guide

### 5.1. Run Automated Test Suite
From the root workspace:
```powershell
cd "backend"
python -m pytest -v
```
*(Runs all 47 tests across Module 1 and Module 2).*

### 5.2. Start FastAPI Backend
```powershell
cd "backend"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
- API Base: `http://127.0.0.1:8000`
- Swagger Docs: `http://127.0.0.1:8000/docs`

### 5.3. Start React Frontend
In a second terminal:
```powershell
cd "frontend"
npm run dev
```
- Open `http://localhost:5173` in your browser.
- Switch between **Digital Twin & Graph (Module 1)** and **Anomaly Detection (Module 2)** using the top navigation bar.

---

## 6. Assumptions & Limitations
1. **Simulated Telemetry**: All metrics are synthetic for cloud resilience simulation. Real live credentials are not required.
2. **Investigation Flag**: An anomaly indicates unusual behavior and triggers an early warning; it is not classified as an outage without supporting evidence.
3. **Integration Ready**: Prepared for Module 3 (Cascading Failure Prediction), Module 4 (Root Cause Analysis), and Module 5 (Diagnostic Agent).
