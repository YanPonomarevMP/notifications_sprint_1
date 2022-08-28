"""Модуль содержит таблицу одиночных email."""
from uuid import uuid4

from sqlalchemy import Column, Integer, DateTime, func, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB

from db.db_init import Base


class SingleEmails(Base):  # type: ignore

    """Таблица SingleEmails."""

    __tablename__ = 'single_emails'
    __table_args__ = {'schema': 'email'}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, nullable=False)
    source = Column(Text, nullable=False)
    destination_id = Column(UUID(as_uuid=True), nullable=False)
    template_id = Column(UUID(as_uuid=True), nullable=False)
    group_id = Column(UUID(as_uuid=True), index=True)
    subject = Column(Text, nullable=False)
    message = Column(JSONB, nullable=False)
    delay = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))
    passed_to_handler_at = Column(DateTime(timezone=True))
    sent_at = Column(DateTime(timezone=True))
    sent_result = Column(Text)
