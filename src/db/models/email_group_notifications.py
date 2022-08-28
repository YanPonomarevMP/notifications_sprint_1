"""Модуль содержит таблицу групповых email."""
from uuid import uuid4

from sqlalchemy import Column, Integer, DateTime, func, Text
from sqlalchemy.dialects.postgresql import UUID, BOOLEAN, JSONB

from db.db_init import Base


class GroupEmails(Base):  # type: ignore

    """Таблица GroupEmails."""

    __tablename__ = 'group_emails'
    __table_args__ = {'schema': 'email'}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, nullable=False)
    source = Column(Text, nullable=False)
    destination_id = Column(UUID(as_uuid=True), nullable=False)
    template_id = Column(UUID(as_uuid=True), nullable=False)
    subject = Column(Text, nullable=False)
    message = Column(JSONB, nullable=False)
    delay = Column(Integer, default=0, nullable=False)
    send_with_gmt = Column(BOOLEAN, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))
    passed_to_handler_at = Column(DateTime(timezone=True))
