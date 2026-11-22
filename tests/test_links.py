from datetime import UTC, datetime, timedelta


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


def test_redirect_records_click_metadata_and_stats(client):
    code = client.post("/links", json={"url": "https://example.com/"}).json()["code"]
    client.get(
        f"/{code}",
        headers={"referer": "https://search.example/", "user-agent": "pytest-agent"},
    )
    client.get(f"/{code}", headers={"referer": "https://search.example/"})
    client.get(f"/{code}", headers={"referer": "https://social.example/"})

    response = client.get(f"/links/{code}/stats")

    assert response.status_code == 200
    stats = response.json()
    assert stats["total_clicks"] == 3
    assert len(stats["clicks_per_day"]) == 7
    assert [day["date"] for day in stats["clicks_per_day"]] == [
        (datetime.now(UTC).date() - timedelta(days=offset)).isoformat()
        for offset in range(6, -1, -1)
    ]
    assert [day["count"] for day in stats["clicks_per_day"][:-1]] == [0] * 6
    assert stats["clicks_per_day"][-1]["count"] == 3
    assert stats["top_referrers"] == [
        {"referrer": "https://search.example/", "count": 2},
        {"referrer": "https://social.example/", "count": 1},
    ]


def test_link_stats_returns_404_for_unknown_code(client):
    response = client.get("/links/missing/stats")

    assert response.status_code == 404


def test_get_link_details(client):
    code = client.post("/links", json={"url": "https://example.com/"}).json()["code"]

    resp = client.get(f"/links/{code}")

    assert resp.status_code == 200
    assert resp.json()["code"] == code
    assert resp.json()["target_url"] == "https://example.com/"
