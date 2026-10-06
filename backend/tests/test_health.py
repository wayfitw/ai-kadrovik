from fastapi.testclient import TestClient

from app import __version__


def test_live(client: TestClient) -> None:
    r = client.get("/health/live")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_readiness_shape(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["version"] == __version__
    assert set(body["checks"]) == {"db", "redis"}
    assert body["status"] in {"ok", "degraded"}
    if all(v == "ok" for v in body["checks"].values()):
        assert body["status"] == "ok"
    else:
        assert body["status"] == "degraded"


def test_readiness_reports_errors(client: TestClient, monkeypatch) -> None:
    from app.api import health

    monkeypatch.setattr(health, "_check_db", lambda: "error")
    monkeypatch.setattr(health, "_check_redis", lambda: "ok")
    body = client.get("/health").json()
    assert body == {
        "status": "degraded",
        "version": __version__,
        "env": "test",
        "checks": {"db": "error", "redis": "ok"},
    }
