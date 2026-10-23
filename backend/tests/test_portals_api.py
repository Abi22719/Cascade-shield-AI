import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.database import get_db, Base, engine, SessionLocal
from app.database.init_db import init_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    init_db(db, force_reset=False)
    db.close()
    yield

def test_admin_portal_api():
    # 1. Summary
    res = client.get("/api/admin/summary")
    assert res.status_code == 200
    data = res.json()
    assert data["total_services"] >= 9
    assert data["platform_uptime_pct"] > 90
    assert data["simulation_mode"] is True

    # 2. Settings get & put
    res_set = client.get("/api/admin/settings")
    assert res_set.status_code == 200
    settings = res_set.json()
    assert "simulation_step_limit" in settings

    res_up = client.put("/api/admin/settings", json={
        "simulation_step_limit": 25,
        "telemetry_refresh_interval_sec": 4
    })
    assert res_up.status_code == 200
    assert res_up.json()["settings"]["simulation_step_limit"] == 25

def test_incident_portal_api():
    # 1. List
    res = client.get("/api/incidents")
    assert res.status_code == 200
    incidents = res.json()
    assert len(incidents) >= 1

    # 2. Detail
    inc_id = incidents[0]["id"]
    res_det = client.get(f"/api/incidents/{inc_id}")
    assert res_det.status_code == 200
    detail = res_det.json()
    assert "affected_services" in detail
    assert "root_cause_candidates" in detail

    # 3. Activity
    res_act = client.get(f"/api/incidents/{inc_id}/activity")
    assert res_act.status_code == 200
    assert len(res_act.json()) >= 1

def test_copilot_portal_api():
    # 1. Payment blast query
    res = client.post("/api/copilot/chat", json={"query": "What happens if the payment service fails?"})
    assert res.status_code == 200
    data = res.json()
    assert "payment" in data["answer"].lower()
    assert len(data["grounded_evidence"]) > 0
    assert data["confidence"] > 0.8
    assert len(data["suggested_actions"]) > 0

    # 2. Recovery comparison query
    res_rec = client.post("/api/copilot/chat", json={"query": "Which recovery plan has lowest risk?"})
    assert res_rec.status_code == 200
    rec_data = res_rec.json()
    assert "lowest" in rec_data["answer"].lower()

def test_developer_portal_api():
    # 1. Health
    res_h = client.get("/api/developer/health")
    assert res_h.status_code == 200
    h_data = res_h.json()
    assert h_data["backend_status"] == "OPERATIONAL"
    assert h_data["database_status"] == "OPERATIONAL"

    # 2. Modules
    res_m = client.get("/api/developer/modules")
    assert res_m.status_code == 200
    modules = res_m.json()
    assert len(modules) == 10
    assert modules[0]["status"] == "OPERATIONAL"

    # 3. Endpoints
    res_e = client.get("/api/developer/endpoints")
    assert res_e.status_code == 200
    assert len(res_e.json()) >= 5

def test_security_portal_api():
    # 1. Roles
    res_r = client.get("/api/security/roles")
    assert res_r.status_code == 200
    roles = res_r.json()["roles"]
    assert "Administrator" in roles
    assert "Cloud Operator" in roles
    assert "Incident Responder" in roles

    # 2. Users
    res_u = client.get("/api/security/users")
    assert res_u.status_code == 200
    users = res_u.json()
    assert len(users) >= 4

    # 3. Audit logs
    res_a = client.get("/api/security/audit")
    assert res_a.status_code == 200
    logs = res_a.json()
    assert len(logs) >= 1

    # 4. Overview
    res_o = client.get("/api/security/overview")
    assert res_o.status_code == 200
    assert res_o.json()["security_posture"] == "COMPLIANT_SECURE"

def test_knowledge_portal_api():
    # 1. List
    res = client.get("/api/knowledge")
    assert res.status_code == 200
    articles = res.json()
    assert len(articles) >= 1

    # 2. Get article
    art_id = articles[0]["id"]
    res_art = client.get(f"/api/knowledge/{art_id}")
    assert res_art.status_code == 200
    assert "content" in res_art.json()

    # 3. Create article
    res_c = client.post("/api/knowledge", json={
        "title": "Test Playbook: Automated Pod Scale-Out",
        "category": "playbook",
        "summary": "Scale out pods on CPU spike",
        "content": "# Automated Pod Scale-out\nTrigger on 85% CPU.",
        "tags": ["scaling", "kubernetes"]
    })
    assert res_c.status_code == 200
    new_id = res_c.json()["article_id"]

    # 4. Search
    res_s = client.get("/api/knowledge?q=Scale-Out")
    assert res_s.status_code == 200
    assert len(res_s.json()) >= 1
