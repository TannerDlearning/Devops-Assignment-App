from tests.conftest import login


def _csrf_for_form(client, path: str = "/create"):
    # Hit a page that renders a form containing csrf_token() so the token exists in session.
    client.get(path)
    with client.session_transaction() as sess:
        return sess.get("csrf_token")


def test_user_can_create_asset(client):
    login(client, "user", "UserPassword123")
    token = _csrf_for_form(client, "/create")

    resp = client.post(
        "/create",
        data={"name": "Dell XPS", "type": "Laptop", "csrf_token": token},
        follow_redirects=False,
    )
    assert resp.status_code == 302


def test_non_admin_cannot_delete(client):
    login(client, "user", "UserPassword123")

    token = _csrf_for_form(client, "/create")
    client.post(
        "/create",
        data={"name": "Phone", "type": "Phone", "csrf_token": token},
        follow_redirects=False,
    )

    # Try delete as non-admin
    token = _csrf_for_form(client, "/")  # dashboard for user won't create token; still OK if token already exists
    if not token:
        token = _csrf_for_form(client, "/create")

    resp = client.post("/delete/1", data={"csrf_token": token})
    assert resp.status_code == 403


def test_admin_can_delete(client):
    login(client, "admin", "AdminPassword123")

    token = _csrf_for_form(client, "/create")
    client.post(
        "/create",
        data={"name": "Monitor", "type": "Monitor", "csrf_token": token},
        follow_redirects=False,
    )

    token = _csrf_for_form(client, "/")
    resp = client.post("/delete/1", data={"csrf_token": token}, follow_redirects=False)
    assert resp.status_code == 302
