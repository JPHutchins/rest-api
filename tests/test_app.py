import json

from tests.conftest import API_BASE_PATH


def test_get_user_exists(client):
    response = client.get(f"{API_BASE_PATH}/users/1")
    data = json.loads(response.data)
    assert data["firstname"] == "J.P."
    assert data["lastname"] == "Hutchins"


def test_get_user_dne(client):
    response = client.get(f"{API_BASE_PATH}/users/99999")
    assert response.status_code == 400
