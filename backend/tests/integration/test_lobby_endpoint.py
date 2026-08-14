from datetime import UTC, datetime, timedelta
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db import get_db
from app.main import app
from app.models.comparison import Comparison
from app.models.lobby import Lobby
from app.models.user import User


def _override_get_db(session: Session):
    def _get_db():
        yield session

    return _get_db


def _make_user(db_session: Session, suffix: str) -> User:
    user = User(
        spotify_id=f"spotify-{uuid4()}",
        display_name=f"Test User {suffix}",
        profile_image_url=f"https://img/{suffix}.jpg",
        access_token="unused",
        refresh_token="unused",
        token_expires_at=datetime.now(UTC) + timedelta(hours=1),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _cleanup(db_session: Session, *user_ids):
    db_session.query(Lobby).filter(Lobby.host_user_id.in_(user_ids)).delete(
        synchronize_session=False
    )
    db_session.query(User).filter(User.id.in_(user_ids)).delete(synchronize_session=False)
    db_session.commit()


def test_get_lobby_creates_empty_lobby_for_new_host(db_session: Session):
    host = _make_user(db_session, "Host")
    host_id = host.id

    app.dependency_overrides[get_db] = _override_get_db(db_session)
    try:
        response = TestClient(app).get(f"/api/lobby/{host_id}")
    finally:
        app.dependency_overrides.pop(get_db, None)
        _cleanup(db_session, host_id)

    assert response.status_code == 200
    body = response.json()
    assert body["host"]["id"] == str(host_id)
    assert body["host"]["display_name"] == "Test User Host"
    assert body["guest"] is None
    assert body["blend_ready"] is False


def test_join_lobby_sets_guest(db_session: Session):
    host = _make_user(db_session, "Host")
    guest = _make_user(db_session, "Guest")
    host_id, guest_id = host.id, guest.id

    app.dependency_overrides[get_db] = _override_get_db(db_session)
    try:
        response = TestClient(app).post(
            f"/api/lobby/join/{host_id}", params={"user_id": str(guest_id)}
        )
    finally:
        app.dependency_overrides.pop(get_db, None)
        _cleanup(db_session, host_id, guest_id)

    assert response.status_code == 200
    body = response.json()
    assert body["guest"]["id"] == str(guest_id)
    assert body["guest"]["display_name"] == "Test User Guest"
    assert body["guest"]["profile_image_url"] == "https://img/Guest.jpg"
    assert body["blend_ready"] is False


def test_second_join_overwrites_previous_guest(db_session: Session):
    host = _make_user(db_session, "Host")
    first_guest = _make_user(db_session, "FirstGuest")
    second_guest = _make_user(db_session, "SecondGuest")
    host_id, first_id, second_id = host.id, first_guest.id, second_guest.id

    app.dependency_overrides[get_db] = _override_get_db(db_session)
    try:
        client = TestClient(app)
        client.post(f"/api/lobby/join/{host_id}", params={"user_id": str(first_id)})
        response = client.post(f"/api/lobby/join/{host_id}", params={"user_id": str(second_id)})
        get_response = client.get(f"/api/lobby/{host_id}")
    finally:
        app.dependency_overrides.pop(get_db, None)
        _cleanup(db_session, host_id, first_id, second_id)

    assert response.json()["guest"]["id"] == str(second_id)
    assert get_response.json()["guest"]["id"] == str(second_id)


def test_join_own_lobby_returns_400(db_session: Session):
    host = _make_user(db_session, "Solo")
    host_id = host.id

    app.dependency_overrides[get_db] = _override_get_db(db_session)
    try:
        response = TestClient(app).post(
            f"/api/lobby/join/{host_id}", params={"user_id": str(host_id)}
        )
    finally:
        app.dependency_overrides.pop(get_db, None)
        _cleanup(db_session, host_id)

    assert response.status_code == 400


def test_get_lobby_returns_404_for_unknown_host(client: TestClient):
    response = client.get(f"/api/lobby/{uuid4()}")

    assert response.status_code == 404


def test_get_lobby_reports_blend_ready_once_comparison_exists(db_session: Session):
    host = _make_user(db_session, "Host")
    guest = _make_user(db_session, "Guest")
    host_id, guest_id = host.id, guest.id

    comparison = Comparison(
        user_a_id=host_id,
        user_b_id=guest_id,
        overall_score=80.0,
        era_score=0.8,
        artist_score=0.8,
        shared_artists=[],
        taste_gaps={},
        era_breakdown=[],
    )
    db_session.add(comparison)
    db_session.commit()

    app.dependency_overrides[get_db] = _override_get_db(db_session)
    try:
        client = TestClient(app)
        client.post(f"/api/lobby/join/{host_id}", params={"user_id": str(guest_id)})
        response = client.get(f"/api/lobby/{host_id}")
    finally:
        app.dependency_overrides.pop(get_db, None)
        db_session.query(Comparison).filter(Comparison.id == comparison.id).delete()
        _cleanup(db_session, host_id, guest_id)

    assert response.json()["blend_ready"] is True


def test_join_lobby_returns_404_for_unknown_guest(db_session: Session):
    host = _make_user(db_session, "Host")
    host_id = host.id

    app.dependency_overrides[get_db] = _override_get_db(db_session)
    try:
        response = TestClient(app).post(
            f"/api/lobby/join/{host_id}", params={"user_id": str(uuid4())}
        )
    finally:
        app.dependency_overrides.pop(get_db, None)
        _cleanup(db_session, host_id)

    assert response.status_code == 404
