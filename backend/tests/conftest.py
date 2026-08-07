import fakeredis
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_db, get_redis
from app.main import app
from app.models import Base

TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture()
def db_session():
    # StaticPool pins every connection to the same in-memory SQLite database;
    # without it, FastAPI's threadpool-executed routes (TestClient calls) can land
    # on a different connection and see a completely separate, table-less :memory: db.
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = session_local()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture()
def fake_redis_client():
    return fakeredis.FakeRedis()


@pytest.fixture()
def client(db_session, fake_redis_client):
    def _get_db_override():
        yield db_session

    def _get_redis_override():
        return fake_redis_client

    app.dependency_overrides[get_db] = _get_db_override
    app.dependency_overrides[get_redis] = _get_redis_override
    original_get_redis = app.state.get_redis
    app.state.get_redis = _get_redis_override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    app.state.get_redis = original_get_redis
