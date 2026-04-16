from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_project_and_ai_ingestion_flow():
    project_response = client.post(
        "/api/v1/projects",
        headers={"x-user-email": "admin@vigorousone.ai"},
        json={"name": "Metro Rail Upgrade", "description": "Gov + vendor transformation"},
    )
    assert project_response.status_code == 200
    project_id = project_response.json()["id"]

    upload_response = client.post(
        "/api/v1/inputs/upload",
        headers={"x-user-email": "admin@vigorousone.ai"},
        json={
            "project_id": project_id,
            "input_type": "meeting",
            "text": "- Vendor to share revised architecture by Friday\n- PMO to review dependency risk register urgently",
            "filename": "kickoff.txt",
        },
    )
    assert upload_response.status_code == 200
    body = upload_response.json()
    assert body["extracted_tasks"] >= 1
    assert "mom_preview" in body


def test_dashboard_endpoint():
    response = client.get("/api/v1/dashboards/control-tower", headers={"x-user-email": "admin@vigorousone.ai"})
    assert response.status_code == 200
    assert "total_tasks" in response.json()
