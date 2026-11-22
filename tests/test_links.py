def test_create_link_returns_short_code(client):
    resp = client.post("/links", json={"url": "https://example.com/some/long/path"})

    assert resp.status_code == 201
    body = resp.json()
    assert len(body["code"]) == 6
    assert body["target_url"] == "https://example.com/some/long/path"


def test_redirect_to_target(client):
    code = client.post("/links", json={"url": "https://example.com/"}).json()["code"]

    resp = client.get(f"/{code}")

    assert resp.status_code == 307
    assert resp.headers["location"] == "https://example.com/"


def test_get_link_details(client):
    code = client.post("/links", json={"url": "https://example.com/"}).json()["code"]

    resp = client.get(f"/links/{code}")

    assert resp.status_code == 200
    assert resp.json()["code"] == code
    assert resp.json()["target_url"] == "https://example.com/"
