"""
Database models and async SQLAlchemy connection
Supports SQLite for zero-config startup and PostgreSQL for production.
Includes transparent column encryption at rest for sensitive case records.
"""

import uuid
from datetime import datetime, timezone
from typing import AsyncGenerator
from sqlalchemy import (
    Column, String, Text, DateTime, ForeignKey, Boolean, JSON, Integer
)
from sqlalchemy.types import TypeDecorator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, relationship
from .config import settings
from .encryption import encrypt_sensitive_text, decrypt_sensitive_text


def utcnow():
    return datetime.now(timezone.utc)


class EncryptedText(TypeDecorator):
    """Transparently encrypts sensitive legal text before saving to DB and decrypts upon query."""
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return encrypt_sensitive_text(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return decrypt_sensitive_text(value)
        return value


# Normalize database URL for async drivers
db_url = settings.DATABASE_URL
if db_url.startswith("sqlite:///"):
    db_url = db_url.replace("sqlite:///", "sqlite+aiosqlite:///")
elif db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg:///")

engine = create_async_engine(
    db_url,
    echo=settings.DEBUG,
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    title = Column(String(255), default="New Legal Consultation")
    language = Column(String(20), default="en")  # "en", "ur", "roman_ur"
    case_category = Column(String(100), default="General Legal Inquiry")
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    user = relationship("User", back_populates="sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan", order_by="Message.created_at")
    case_summary = relationship("CaseSummary", back_populates="session", uselist=False, cascade="all, delete-orphan")
    documents = relationship("UploadedDocument", back_populates="session", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # "user", "assistant", "system"
    content = Column(EncryptedText, nullable=False)  # Encrypted at rest
    structured_data = Column(JSON, nullable=True)  # intake extraction data
    citations = Column(JSON, nullable=True)  # retrieved law sections
    is_emergency = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    session = relationship("ChatSession", back_populates="messages")


class CaseSummary(Base):
    __tablename__ = "case_summaries"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("chat_sessions.id", ondelete="CASCADE"), unique=True, nullable=False)
    issue_type = Column(String(200), default="Pending Clarification")
    parties = Column(String(255), default="Undisclosed")
    dates = Column(String(255), default="Undisclosed")
    location_province = Column(String(100), default="Federal / Unspecified")
    documents_mentioned = Column(JSON, default=list)
    stage = Column(String(50), default="intake_clarifying")  # "intake_clarifying", "ready_for_advice", "completed"
    applicable_laws = Column(JSON, default=list)
    next_steps = Column(JSON, default=list)
    evidence_checklist = Column(JSON, default=list)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    session = relationship("ChatSession", back_populates="case_summary")


class UploadedDocument(Base):
    __tablename__ = "uploaded_documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(100), nullable=False)
    file_path = Column(String(500), nullable=False)
    extracted_text = Column(EncryptedText, default="")  # Encrypted at rest
    created_at = Column(DateTime(timezone=True), default=utcnow)

    session = relationship("ChatSession", back_populates="documents")


class EmergencyLog(Base):
    __tablename__ = "emergency_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), nullable=True)
    trigger_reason = Column(String(100), nullable=False)
    user_message = Column(EncryptedText, nullable=False)  # Encrypted at rest
    timestamp = Column(DateTime(timezone=True), default=utcnow)


class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    session_id = Column(String(36), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=True, index=True)
    message_id = Column(String(36), ForeignKey("messages.id", ondelete="SET NULL"), nullable=True, index=True)
    feedback_type = Column(String(50), nullable=False)  # "citation_wrong", "reasoning_wrong", "looks_fine", "thumbs_up", "thumbs_down"
    category = Column(String(50), default="general")  # "statute_accuracy", "direction", "hallucination", "clarity", "general"
    comment = Column(EncryptedText, nullable=True)  # Confidential feedback comment encrypted at rest
    query_excerpt = Column(String(500), nullable=True)
    citations_flagged = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), default=utcnow)


async def init_db():
    """Create all tables asynchronously."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for obtaining async db session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
