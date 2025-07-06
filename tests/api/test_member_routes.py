from datetime import datetime
from uuid import uuid4

from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)

# Common fake member data
test_line_id = "TEST_LINE_ID_001"
test_member_payload = {
    "member_id": str(uuid4()),
    "line_id": test_line_id,
    "member_name": "測試用戶",
    "create_at": datetime.now().isoformat(),
    "phone": "0912345678",
    "order_type": "預付",
    "remain_delivery": 2,
    "remain_volume": 5,
    "prepaid": 1000,
    "valid_member": True,
}


def test_create_member():
    res = client.post("/api/members/", json=test_member_payload)
    assert res.status_code == 200
    assert res.json()["status"] == "success"
    assert res.json()["data"]["line_id"] == test_line_id


def test_get_member_by_line_id():
    res = client.get(f"/api/members/by-line-id/{test_line_id}")
    assert res.status_code == 200
    assert res.json()["data"]["member_name"] == "測試用戶"


def test_update_member():
    res = client.put(
        f"/api/members/by-line-id/{test_line_id}",
        json={"remain_delivery": 999, "valid_member": True},
    )
    assert res.status_code == 200
    assert res.json()["data"]["remain_delivery"] == 999


def test_delete_member():
    res = client.delete(f"/api/members/by-line-id/{test_line_id}")
    assert res.status_code == 200


def test_deleted_member_should_be_invalid():
    res = client.get(f"/api/members/by-line-id/{test_line_id}")
    assert res.status_code == 200
    assert res.json()["data"]["valid_member"] is False
