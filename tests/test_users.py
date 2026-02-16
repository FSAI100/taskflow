def test_register_and_login(client):
    # 注册
    res = client.post("/users/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "test123",
    })
    assert res.status_code == 201
    assert res.json()["username"] == "testuser"

    # 登录
    res = client.post("/users/login", json={
        "username": "testuser",
        "password": "test123",
    })
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_duplicate_username(client):
    client.post("/users/register", json={"username": "dup", "email": "a@b.com", "password": "123"})
    res = client.post("/users/register", json={"username": "dup", "email": "b@b.com", "password": "123"})
    assert res.status_code == 400
