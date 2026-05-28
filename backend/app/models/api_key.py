# models/api_key.py
# API keys are how developers authenticate inference requests
# SECURITY: We never store the raw key — only a hash

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class APIKey(Base):
    __tablename__ = "api_keys"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Human readable name — "my-prod-key", "test-key"
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="default"
    )

    # Prefix shown in UI — "sk-inf-ab12****"
    # Never reveals the full key
    key_prefix: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    # SHA256 hash of the full key
    # Raw key shown ONCE to user then discarded
    key_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    last_used_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # Optional expiry — None means never expires
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationship back to user
    user = relationship("User", back_populates="api_keys")

    __table_args__ = (
        Index("idx_api_keys_key_hash", "key_hash"),
        Index("idx_api_keys_user_id", "user_id"),
    )

    def __repr__(self):
        return f"<APIKey {self.key_prefix}****>"