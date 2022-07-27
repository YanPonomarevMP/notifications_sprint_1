"""
Модуль содержит таблицу одиночных email.
"""
from uuid import uuid4

from sqlalchemy import Table, Column, Integer, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSON

from db.db_init import Base

group_emails = Table(
    'group_emails',
    Base.metadata,
    Column('id', UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, nullable=False),
    Column('destination_id', UUID(as_uuid=True), nullable=False),
    Column('template_id', UUID(as_uuid=True), nullable=False),
    Column('message', JSON, nullable=False),
    Column('delay', Integer, default=0, nullable=False),
    Column('created_at', DateTime(timezone=True), default=func.now()),
    Column('updated_at', DateTime(timezone=True), onupdate=func.now()),
    Column('deleted_at', DateTime(timezone=True)),
    Column('passed_to_handler', DateTime(timezone=True)),
    schema='email'
)
