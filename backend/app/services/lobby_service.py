from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.lobby import Lobby
from app.models.user import User


def get_or_create_lobby(db: Session, host: User) -> Lobby:
    lobby = db.query(Lobby).filter(Lobby.host_user_id == host.id).one_or_none()
    if lobby is None:
        lobby = Lobby(host_user_id=host.id)
        db.add(lobby)
        db.commit()
        db.refresh(lobby)
    return lobby


def join_lobby(db: Session, host: User, guest: User) -> Lobby:
    lobby = get_or_create_lobby(db, host)
    # Last-write-wins: a lobby holds exactly one guest at a time. A new
    # joiner simply replaces whoever was there before.
    lobby.guest_user_id = guest.id
    lobby.updated_at = datetime.now(UTC)
    db.commit()
    db.refresh(lobby)
    return lobby
