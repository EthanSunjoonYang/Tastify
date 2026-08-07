import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db import Base


class Comparison(Base):
    __tablename__ = "comparisons"
    __table_args__ = (UniqueConstraint("user_a_id", "user_b_id"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_a_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    user_b_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    era_score: Mapped[float] = mapped_column(Float, nullable=False)
    artist_score: Mapped[float] = mapped_column(Float, nullable=False)
    shared_artists: Mapped[list[dict]] = mapped_column(JSONB, nullable=False)
    taste_gaps: Mapped[dict] = mapped_column(JSONB, nullable=False)
    era_breakdown: Mapped[list[dict]] = mapped_column(JSONB, nullable=False)
    playlist_track_ids: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)
    spotify_playlist_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
