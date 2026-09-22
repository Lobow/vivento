from datetime import UTC, datetime, timedelta


def _future_iso(days=5):
    return (datetime.now(UTC) + timedelta(days=days)).isoformat()


def _past_iso(days=5):
    return (datetime.now(UTC) - timedelta(days=days)).isoformat()


def _event_payload(**overrides):
    payload = {
        "name": "Feira de Tecnologia",
        "description": "Um evento sobre tecnologia",
        "date_time": _future_iso(),
        "location": "Centro de Convenções",
        "capacity": 2,
    }
    payload.update(overrides)
    return payload


def test_create_event_requires_authentication(client):
    response = client.post("/events", json=_event_payload())
    assert response.status_code == 401


def test_create_event_success(client, auth_headers):
    response = client.post(
        "/events",
        data=_event_payload(),
        files={"file": ("cover.png", b"\x89PNG\r\n\x1a\n123", "image/png")},
        headers=auth_headers,
    )
    assert response.status_code == 201


def test_create_event_invalid_capacity_fails(client, auth_headers):
    response = client.post("/events", json=_event_payload(capacity=0), headers=auth_headers)
    assert response.status_code == 422


def test_list_events(client, auth_headers):
    client.post(
        "/events",
        data=_event_payload(name="Evento A"),
        files={"file": ("cover.png", b"\x89PNG\r\n\x1a\n123", "image/png")},
        headers=auth_headers,
    )
    client.post(
        "/events",
        data=_event_payload(name="Evento B"),
        files={"file": ("cover.png", b"\x89PNG\r\n\x1a\n123", "image/png")},
        headers=auth_headers,
    )
    response = client.get("/events")
    assert response.status_code == 200


def test_get_event_not_found(client):
    response = client.get("/events/inexistente")
    assert response.status_code == 404


def test_update_event_by_owner(client, auth_headers):
    created = client.post(
        "/events",
        data=_event_payload(),
        files={"file": ("cover.png", b"\x89PNG\r\n\x1a\n123", "image/png")},
        headers=auth_headers,
    ).json()
    response = client.put(
        f"/events/{created['id']}",
        data=_event_payload(),
        files={"file": ("cover.png", b"\x89PNG\r\n\x1a\n123", "image/png")},
        headers=auth_headers,
    )
    assert response.status_code == 200


def test_update_event_requires_authentication(client, auth_headers):
    created = client.post(
        "/events",
        data=_event_payload(),
        files={"file": ("cover.png", b"\x89PNG\r\n\x1a\n123", "image/png")},
        headers=auth_headers,
    ).json()
    response = client.put(f"/events/{created['id']}", data={"name": "Novo Nome"})
    assert response.status_code == 401


def test_delete_event_by_owner(client, auth_headers):
    created = client.post(
        "/events",
        data=_event_payload(),
        files={"file": ("cover.png", b"\x89PNG\r\n\x1a\n123", "image/png")},
        headers=auth_headers,
    ).json()
    response = client.delete(f"/events/{created['id']}", headers=auth_headers)
    assert response.status_code == 204
    assert client.get(f"/events/{created['id']}").status_code == 404


def test_filter_events_by_status_past(client, auth_headers):
    client.post(
        "/events",
        data=_event_payload(name="Evento Passado", date_time=_past_iso()),
        files={"file": ("cover.png", b"\x89PNG\r\n\x1a\n123", "image/png")},
        headers=auth_headers,
    )
    client.post(
        "/events",
        json=_event_payload(name="Evento Futuro", date_time=_future_iso()),
        files={"file": ("cover.png", b"\x89PNG\r\n\x1a\n123", "image/png")},
        headers=auth_headers,
    )
    response = client.get("/events", params={"status": "past"})
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["name"] == "Evento Passado"


def test_filter_events_by_status_full(client, auth_headers):
    event = client.post(
        "/events",
        data=_event_payload(capacity=1),
        files={"file": ("cover.png", b"\x89PNG\r\n\x1a\n123", "image/png")},
        headers=auth_headers,
    ).json()

    client.post(
        f"/events/{event['id']}/participants",
        json={"name": "Participante 1", "email": "p1@teste.com"},
    )

    response = client.get("/events", params={"status": "full"})
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["status"] == "full"
