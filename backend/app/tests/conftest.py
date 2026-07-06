import fakeredis
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import redis_client as redis_module
from app.db.session import Base


@pytest.fixture()
def db_session():
    """
    Fresh in-memory SQLite database per test.

    Using SQLite in tests (instead of spinning up real Postgres) keeps the
    integration test suite fast and hermetic in CI, while still exercising the
    real SQLAlchemy models/queries -- only the underlying engine differs.
    """
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(autouse=True)
def fake_redis(monkeypatch):
    """
    Swap the real Redis client for an in-memory fake so tests never require a
    running Redis instance, but still exercise the actual cache-aside code
    paths in services/shortener.py.
    """
    fake = fakeredis.FakeStrictRedis(decode_responses=True)
    monkeypatch.setattr(redis_module, "redis_client", fake)
    yield fake
