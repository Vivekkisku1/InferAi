# models/usage_log.py
# Every inference request is logged here
# Used for billing, analytics, and abuse detection

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Numeric, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class UsageLog(Base):
    __tablename__ = "usage_logs"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    api_key_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("api_keys.id"),
        nullable=True  # nullable in case key deleted
    )

    # Which model was called
    model_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    # Token counts for billing
    input_tokens: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    output_tokens: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    # What we charged the user in USD
    total_cost_usd: Mapped[float] = mapped_column(
        Numeric(12, 8),
        default=0,
        nullable=False
    )

    # Response time in milliseconds
    latency_ms: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    # success | error | rate_limited
    status: Mapped[str] = mapped_column(
        String(50),
        default="success",
        nullable=False
    )

    # Only populated on errors — never log user prompts here
    error_message: Mapped[str] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )

    # Relationships
    user = relationship("User", back_populates="usage_logs")

    __table_args__ = (
        Index("idx_usage_logs_user_id", "user_id"),
        Index("idx_usage_logs_created_at", "created_at"),
        Index("idx_usage_logs_model_id", "model_id"),
    )

    def __repr__(self):
        return f"<UsageLog {self.user_id} {self.model_id}>"