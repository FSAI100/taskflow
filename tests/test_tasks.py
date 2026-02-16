import pytest


@pytest.fixture
def auth_headers(client):
    """Register, login, return Authorization headers."""
    client.post("/users/register", json={
        "username": "taskuser",
        "email": "task@example.com",
        "password": "test123",
    })
    login = client.post("/users/login", json={
        "username": "taskuser",
        "password": "test123",
    })
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_and_list_tasks(client, auth_headers):
    res = client.post("/tasks/", json={
        "title": "写周报",
        "description": "周五前完成",
        "priority": "high",
        "status": "todo",
    }, headers=auth_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["title"] == "写周报"
    assert data["priority"] == "high"

    res = client.get("/tasks/", headers=auth_headers)
    assert res.status_code == 200
    tasks = res.json()
    assert len(tasks) >= 1
    titles = [t["title"] for t in tasks]
    assert "写周报" in titles


def test_get_update_delete_task(client, auth_headers):
    create = client.post("/tasks/", json={
        "title": "待删除任务",
        "priority": "medium",
        "status": "todo",
    }, headers=auth_headers)
    assert create.status_code == 201
    task_id = create.json()["id"]

    res = client.get(f"/tasks/{task_id}", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["title"] == "待删除任务"

    res = client.put(f"/tasks/{task_id}", json={"status": "done", "title": "已完成任务"}, headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["status"] == "done"
    assert res.json()["title"] == "已完成任务"

    res = client.delete(f"/tasks/{task_id}", headers=auth_headers)
    assert res.status_code == 204

    res = client.get(f"/tasks/{task_id}", headers=auth_headers)
    assert res.status_code == 404
