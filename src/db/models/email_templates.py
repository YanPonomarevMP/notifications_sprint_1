"""
Модуль содержит таблицу HTML шаблонов email.
"""
from uuid import uuid4

from sqlalchemy import Column, DateTime, func, Text
from sqlalchemy.dialects.postgresql import UUID

from db.db_init import Base


class HTMLTemplates(Base):
    __tablename__ = 'html_templates'
    __table_args__ = {'schema': 'email'}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, nullable=False)
    title = Column(Text, nullable=False)
    template = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    deleted_at = Column(DateTime(timezone=True))
