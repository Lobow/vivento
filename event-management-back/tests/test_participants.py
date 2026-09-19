from datetime import UTC, datetime, timedelta


def _create_event(client, auth_headers, capacity=2):
    payload = {
        "name": "Workshop de Python",
        "description": "Aprenda Python do zero",
        "date_time": (datetime.now(UTC) + timedelta(days=3)).isoformat(),
        "location": "Sala 1",
        "capacity": capacity,
    }
    return client.post("/events", json=payload, headers=auth_headers).json()


def test_register_participant_success(client, auth_headers):
    event = _create_event(client, auth_headers)
    response = client.post(
        f"/events/{event['id']}/participants",
        json={"name": "João", "email": "joao@teste.com"},
    )
    assert response.status_code == 201
    assert response.json()["email"] == "joao@teste.com"


def test_register_participant_duplicate_email_fails(client, auth_headers):
    event = _create_event(client, auth_headers)
    payload = {"name": "João", "email": "joao@teste.com"}
    client.post(f"/events/{event['id']}/participants", json=payload)
    response = client.post(f"/events/{event['id']}/participants", json=payload)
    assert response.status_code == 409


def test_register_participant_respects_capacity(client, auth_headers):
    event = _create_event(client, auth_headers, capacity=1)
    client.post(
        f"/events/{event['id']}/participants",
        json={"name": "João", "email": "joao@teste.com"},
    )
    response = client.post(
        f"/events/{event['id']}/participants",
        json={"name": "Maria", "email": "maria@teste.com"},
    )
    assert response.status_code == 409
    assert "lotado" in response.json()["detail"].lower()


def test_list_participants(client, auth_headers):
    event = _create_event(client, auth_headers)
    client.post(
        f"/events/{event['id']}/participants",
        json={"name": "João", "email": "joao@teste.com"},
    )
    response = client.get(f"/events/{event['id']}/participants")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_register_participant_event_not_found(client):
    response = client.post(
        "/events/inexistente/participants",
        json={"name": "João", "email": "joao@teste.com"},
    )
    assert response.status_code == 404


def test_remove_participant_requires_auth(client, auth_headers):
    event = _create_event(client, auth_headers)
    participant = client.post(
        f"/events/{event['id']}/participants",
        json={"name": "João", "email": "joao@teste.com"},
    ).json()
    response = client.delete(f"/events/{event['id']}/participants/{participant['id']}")
    assert response.status_code == 401


def test_remove_participant_by_owner(client, auth_headers):
    event = _create_event(client, auth_headers)
    participant = client.post(
        f"/events/{event['id']}/participants",
        json={"name": "João", "email": "joao@teste.com"},
    ).json()
    response = client.delete(
        f"/events/{event['id']}/participants/{participant['id']}", headers=auth_headers
    )
    assert response.status_code == 204
