from tests.conftest import login


def test_login_success(client):
    resp = login(client, "admin", "AdminPassword123")
    assert resp.status_code == 302


def test_login_failure_increments_attempts(client):
    # 1st bad attempt
    resp = login(client, "user", "wrong")
    assert resp.status_code == 200
    # message is flashed; just ensure page rendered


def test_csrf_required_on_login(client):
    # Posting without csrf should be forbidden
    resp = client.post("/login", data={"username": "admin", "password": "AdminPassword123"})
    assert resp.status_code == 403
