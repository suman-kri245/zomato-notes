from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from datetime import datetime

from backend.database import Base


# ============================================================
# USER MODEL
# ============================================================

class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    name = Column(
        String,
        nullable=False,
    )

    email = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
    )

    password = Column(
        String,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    notes = relationship(
        "Note",
        back_populates="owner",
        cascade="all, delete-orphan",
    )


# ============================================================
# NOTE MODEL
# ============================================================

class Note(Base):
    __tablename__ = "notes"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    title = Column(
        String(120),
        nullable=False,
    )

    content = Column(
        Text,
        nullable=False,
    )

    tag = Column(
        String,
        nullable=True,
    )

    owner_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    owner = relationship(
        "User",
        back_populates="notes",
    )