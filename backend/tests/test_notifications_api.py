import pytest
from fastapi.testclient import TestClient

def test_notifications_list_api(client: TestClient):
    res = client.get("/api/notifications")
    assert res.status_code == 200
    data = res.json()
    assert "unread_count" in data
    assert "total_count" in data
    assert "notifications" in data
    assert isinstance(data["notifications"], list)

def test_notification_mark_read_and_read_all(client: TestClient):
    res = client.get("/api/notifications")
    notifs = res.json()["notifications"]
    if len(notifs) > 0:
        first_id = notifs[0]["id"]
        # Mark single as read
        read_res = client.post(f"/api/notifications/{first_id}/read")
        assert read_res.status_code == 200
        assert read_res.json()["read_status"] is True

    # Mark all as read
    all_res = client.post("/api/notifications/read-all")
    assert all_res.status_code == 200
    assert "marked_read_count" in all_res.json()

def test_notification_not_found(client: TestClient):
    res = client.post("/api/notifications/invalid-id-xyz/read")
    assert res.status_code == 404
