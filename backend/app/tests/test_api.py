import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import Base, get_db
from app.main import app


@pytest.fixture()
def client(fake_redis):
    """
    Full API-level test client with the DB dependency overridden to use an
    isolated in-memory SQLite instance, so these tests exercise the real
    FastAPI routing/validation layer without needing Postgres running.

    StaticPool is required here: SQLite's `:memory:` database normally lives
    only on a single connection, so without it every new connection from the
    pool would see a fresh, empty database (causing "no such table" errors).
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


class TestHealthCheck:
    def test_health_endpoint(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


class TestShortenEndpoint:
    def test_shorten_returns_short_code(self, client):
        response = client.post("/api/shorten", json={"long_url": "https://example.com/some/page"})

        assert response.status_code == 201
        body = response.json()
        assert body["long_url"] == "https://example.com/some/page"
        assert len(body["short_code"]) > 0
        assert body["short_code"] in body["short_url"]

    def test_shorten_rejects_invalid_url(self, client):
        response = client.post("/api/shorten", json={"long_url": "not-a-url"})
        assert response.status_code == 422


class TestRedirectEndpoint:
    def test_redirect_follows_to_long_url(self, client):
        create_response = client.post("/api/shorten", json={"long_url": "https://example.com/redirect-me"})
        short_code = create_response.json()["short_code"]

        redirect_response = client.get(f"/{short_code}", follow_redirects=False)
        assert redirect_response.status_code == 307
        assert redirect_response.headers["location"] == "https://example.com/redirect-me"

    def test_unknown_code_returns_404(self, client):
        response = client.get("/doesnotexist123", follow_redirects=False)
        assert response.status_code == 404


class TestAnalyticsEndpoint:
    def test_analytics_reflects_recorded_clicks(self, client):
        create_response = client.post("/api/shorten", json={"long_url": "https://example.com/track-me"})
        short_code = create_response.json()["short_code"]

        client.get(f"/{short_code}", follow_redirects=False)
        client.get(f"/{short_code}", follow_redirects=False)

        analytics_response = client.get(f"/api/analytics/{short_code}")
        assert analytics_response.status_code == 200
        assert analytics_response.json()["total_clicks"] == 2

    def test_analytics_for_unknown_code_returns_404(self, client):
        response = client.get("/api/analytics/doesnotexist")
        assert response.status_code == 404
