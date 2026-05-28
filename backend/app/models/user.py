# models/user.py
# Defines the users table — your customers who sign up for the platform

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, Numeric, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    # Primary key — UUID is better than integer for security
    # (attackers can't enumerate users by ID)
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    # Never store plain text passwords — always hashed
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=True
    )

    # Plan controls what features user can access
    plan: Mapped[str] = mapped_column(
        String(50),
        default="free",
        nullable=False
    )

    # Credits in USD — prepaid balance model
    credits: Mapped[float] = mapped_column(
        Numeric(12, 6),
        default=5.00,
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    # Track if email is verified — important for security
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    api_keys = relationship(
        "APIKey",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    usage_logs = relationship(
        "UsageLog",
        back_populates="user"
    )

    # Indexes for fast queries
    __table_args__ = (
        Index("idx_users_email", "email"),
        Index("idx_users_plan", "plan"),
    )

    def __repr__(self):
        return f"<User {self.email}>"