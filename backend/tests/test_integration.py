from uuid import uuid4

import httpx
from httpx import ASGITransport

from app.main import app


transport = ASGITransport(app=app)
client = httpx.AsyncClient(transport=transport, base_url="http://test")


import pytest


@pytest.mark.anyio
async def test_health_and_security_headers():
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json().get("status") == "ok"
    assert response.headers.get("x-content-type-options") == "nosniff"
    assert response.headers.get("x-frame-options") == "DENY"
    assert response.headers.get("referrer-policy") == "strict-origin-when-cross-origin"


@pytest.mark.anyio
async def test_auth_register_login_and_me_flow():
    unique = uuid4().hex[:10]
    identifier = f"{unique}@example.com"
    password = "StrongPass1"
    register_payload = {
        "name": "Integration User",
        "age": "22",
        "identifier": identifier,
        "password": password,
    }

    register_response = await client.post("/users/register", json=register_payload)
    assert register_response.status_code == 200
    register_data = register_response.json()
    assert register_data.get("status") == "success"
    token = register_data.get("token")
    assert token

    login_response = await client.post(
        "/users/login",
        json={"identifier": identifier, "password": password},
    )
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert login_data.get("status") == "success"
    login_token = login_data.get("token")
    assert login_token

    me_response = await client.get(

        "/users/me",
        headers={"Authorization": f"Bearer {login_token}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["user"]["identifier"] == identifier

    update_response = await client.put(
        "/users/me",
        headers={"Authorization": f"Bearer {login_token}"},
        json={"name": "Updated Integration User", "age": "23"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["profile"]["name"] == "Updated Integration User"


@pytest.mark.anyio
async def test_dataset_selection_and_prediction_contract():
    datasets_response = await client.get("/analytics/datasets")

    assert datasets_response.status_code == 200
    datasets_data = datasets_response.json()
    assert len(datasets_data.get("datasets", [])) == 4

    first_dataset = datasets_data["datasets"][0]
    select_response = await client.post(

        "/analytics/datasets/select",
        json={"dataset_name": first_dataset},
    )
    assert select_response.status_code == 200
    assert select_response.json().get("status") == "success"

    mode_response = await client.post(

        "/analytics/dataset-mode",
        json={"mode": "synthetic_demo"},
    )
    assert mode_response.status_code == 200
    assert mode_response.json().get("mode") == "synthetic_demo"

    prediction_response = await client.get("/predictions/next-hour")
    assert prediction_response.status_code == 200
    prediction_data = prediction_response.json()
    assert "prediction" in prediction_data
    assert "anomaly_summary" in prediction_data




@pytest.mark.anyio
async def test_chatbot_nlp_fallback_intent():

    response = await client.post(
        "/chatbot/chat",
        params={"message": "which ai model is currently active in this project"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data.get("intent") == "model_info"
