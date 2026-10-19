import pytest
from fastapi.testclient import TestClient

def test_reports_list_and_generate(client: TestClient):
    # List reports
    list_res = client.get("/api/reports")
    assert list_res.status_code == 200
    data = list_res.json()
    assert "total" in data
    assert "reports" in data

    # Generate a report
    gen_payload = {
        "report_type": "incident_lifecycle",
        "report_title": "Automated Test Incident Audit",
        "data_source": "simulated",
        "report_format": "markdown"
    }
    gen_res = client.post("/api/reports/generate", json=gen_payload)
    assert gen_res.status_code == 200
    rep = gen_res.json()
    assert rep["report_title"] == "Automated Test Incident Audit"
    assert rep["report_type"] == "incident_lifecycle"
    assert "CascadeShield AI" in rep["content"]
    rep_id = rep["id"]

    # Get single report
    get_res = client.get(f"/api/reports/{rep_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == rep_id

    # Export JSON
    json_export = client.get(f"/api/reports/{rep_id}/export/json")
    assert json_export.status_code == 200
    assert json_export.json()["report_id"] == rep_id

    # Export CSV
    csv_export = client.get(f"/api/reports/{rep_id}/export/csv")
    assert csv_export.status_code == 200
    assert "Report ID" in csv_export.text

def test_report_not_found(client: TestClient):
    assert client.get("/api/reports/non-existent-report").status_code == 404
    assert client.get("/api/reports/non-existent-report/export/csv").status_code == 404
    assert client.get("/api/reports/non-existent-report/export/json").status_code == 404
