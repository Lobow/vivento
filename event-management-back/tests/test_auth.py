def test_register_user(client):
    response = client.post(
        "/auth/register",
        json={"name": "Ana Silva", "email": "ana@teste.com", "password": "senha123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "ana@teste.com"
    assert "hashed_password" not in data


def test_register_duplicate_email_fails(client):
    payload = {"name": "Ana Silva", "email": "ana@teste.com", "password": "senha123"}
    client.post("/auth/register", json=payload)
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 409


def test_login_success(client):
    client.post(
        "/auth/register",
        json={"name": "Ana Silva", "email": "ana@teste.com", "password": "senha123"},
    )
    response = client.post(
        "/auth/token", data={"username": "ana@teste.com", "password": "senha123"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_wrong_password_fails(client):
    client.post(
        "/auth/register",
        json={"name": "Ana Silva", "email": "ana@teste.com", "password": "senha123"},
    )
    response = client.post("/auth/token", data={"username": "ana@teste.com", "password": "errada"})
    assert response.status_code == 401


def test_me_requires_authentication(client):
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_me_with_valid_token(client, auth_headers):
    response = client.get("/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "organizador@teste.com"
