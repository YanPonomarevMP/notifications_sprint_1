"""
Модуль содержит таблицу HTML шаблонов email.
"""
from uuid import uuid4

from sqlalchemy import Table, Column, DateTime, func, Text
from sqlalchemy.dialects.postgresql import UUID

from db.db_init import Base

templates = Table(
    'templates',
    Base.metadata,
    Column('id', UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, nullable=False),
    Column('template', Text, nullable=False),
    Column('created_at', DateTime(timezone=True), default=func.now()),
    Column('updated_at', DateTime(timezone=True), onupdate=func.now()),
    schema='email'
)
