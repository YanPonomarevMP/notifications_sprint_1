"""Модуль содержит CRUD для работы с шаблонами email сообщений"""
from fastapi import Response
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import delete, update, func, and_, select
from sqlalchemy.dialects.postgresql import insert

from config.settings import config
from db.message_brokers.rabbit_message_broker import message_broker_factory
from db.models.email_group_notifications import GroupEmails
from db.models.email_templates import HTMLTemplates
from db.storage.orm_factory import get_db, AsyncPGClient
from notifier_api.models.http_responses import http  # type: ignore
from notifier_api.models.message_broker_models import MessageBrokerData
from notifier_api.models.notifier_group_emails import GroupEmailsResponse, GroupEmailsRequest, GroupEmailsQuery, \
    GroupEmailsResponseSelected, GroupEmailsRequestUpdate, GroupEmailsSelected
from notifier_api.services.emails_factory import get_emails_factory, EmailsFactory
from utils.custom_exceptions import DataBaseError
from utils.custom_fastapi_router import LoggedRoute
from utils.dependencies import requests_per_minute

router = APIRouter(
    prefix='/group_emails',
    route_class=LoggedRoute,
)


@router.post(
    path='/',
    status_code=http.accepted.code,
    response_model=GroupEmailsResponse,
    summary='Create new email',
    description='Endpoint accepts email for processing',
    response_description='Returns the answer whether the email accepted but not sent yet',
    dependencies=[Depends(requests_per_minute(3))]
)
async def new_email(
    single_email: GroupEmailsRequest,
    factory: EmailsFactory = Depends(get_emails_factory),
    idempotency_key: UUID = Header(description='UUID4'),  # noqa: B008
    x_request_id: str = Header(),  # noqa: B008, WPS204
) -> GroupEmailsResponse:

    query_data = GroupEmailsQuery(**single_email.dict())
    query_data.id = idempotency_key

    query = insert(GroupEmails)
    query = query.returning(GroupEmails.created_at)
    query = query.values(**query_data.dict(exclude={'msg', 'emails_selected'}))
    idempotent_query = query.on_conflict_do_nothing(index_elements=['id'])

    message_to_broker = MessageBrokerData(
        message_body=query_data.id,
        queue_name=config.rabbit_mq.queue_raw_single_messages,
        message_headers={'x-request-id': x_request_id},
        delay=query_data.delay
    )

    query_data.msg = await factory.insert(idempotent_query, message_to_broker)

    return query_data


@router.put(
    path='/',
    status_code=http.ok.code,
    response_model=GroupEmailsResponse,
    summary='Create new email',
    description='Endpoint accepts email for processing',
    response_description='Returns the answer whether the email accepted but not sent yet',
    dependencies=[Depends(requests_per_minute(3))]
)
async def update_email(
    single_email: GroupEmailsRequestUpdate,
    response: Response,
    factory: EmailsFactory = Depends(get_emails_factory),
) -> GroupEmailsResponse:

    query_data = GroupEmailsQuery(**single_email.dict())

    query = update(GroupEmails)
    query = query.returning(GroupEmails.created_at)
    query = query.filter(
        and_(
            GroupEmails.id == query_data.id,
            GroupEmails.deleted_at == None,  # noqa: E711
            GroupEmails.passed_to_handler_at == None  # noqa: E711
        )
    )
    query = query.values(**query_data.dict(exclude={'msg', 'emails_selected', 'id'}))

    query_data.msg = await factory.update(query, response)

    return query_data


@router.delete(
    path='/{email_id}',
    status_code=http.ok.code,
    response_model=GroupEmailsResponse,
    summary='Delete email',
    description='Endpoint delete email from database before send',
    response_description='Returns the answer whether the email is deleted',
    dependencies=[Depends(requests_per_minute(3))]
)
async def delete_email(
    email_id: UUID,
    response: Response,
    factory: EmailsFactory = Depends(get_emails_factory),
) -> GroupEmailsResponse:

    query_data = GroupEmailsQuery(id=email_id)

    query = update(GroupEmails)
    query = query.returning(GroupEmails.deleted_at)
    query = query.filter(
        and_(
            GroupEmails.id == query_data.id,
            GroupEmails.deleted_at == None,  # noqa: E711
            GroupEmails.passed_to_handler_at == None  # noqa: E711
        )
    )
    query = query.values(deleted_at=func.now())

    query_data.msg = await factory.delete(query, response)

    return query_data


@router.get(
    path='/{email_id}',
    status_code=http.ok.code,
    response_model=GroupEmailsResponseSelected,
    summary='Get one email',
    description='Endpoint returns email data from database',
    response_description='Email data',
    dependencies=[Depends(requests_per_minute(3))]
)
async def get_email(
    email_id: UUID,
    response: Response,
    factory: EmailsFactory = Depends(get_emails_factory),
) -> GroupEmailsResponse:

    query_data = GroupEmailsQuery(id=email_id)

    query = select(
        GroupEmails.id,
        GroupEmails.source,
        GroupEmails.destination_id,
        GroupEmails.template_id,
        GroupEmails.subject,
        GroupEmails.message,
        GroupEmails.delay,
        GroupEmails.send_with_gmt
    )
    query = query.filter(
        and_(
            GroupEmails.id == query_data.id,
            GroupEmails.deleted_at == None  # noqa: E711
        )
    )

    query_data.msg, query_data.emails_selected = await factory.select(query, response, GroupEmailsSelected)

    return query_data


@router.get(
    path='/',
    status_code=http.ok.code,
    response_model=GroupEmailsResponseSelected,
    summary='Get all emails',
    description='Endpoint returns all emails data from database',
    response_description='emails data',
    dependencies=[Depends(requests_per_minute(3))]
)
async def get_all_emails(
    response: Response,
    factory: EmailsFactory = Depends(get_emails_factory),
) -> GroupEmailsResponse:

    query_data = GroupEmailsQuery()

    query = select(
        GroupEmails.id,
        GroupEmails.source,
        GroupEmails.destination_id,
        GroupEmails.template_id,
        GroupEmails.subject,
        GroupEmails.message,
        GroupEmails.delay,
        GroupEmails.send_with_gmt
    )
    query = query.filter(
        and_(
            GroupEmails.deleted_at == None  # noqa: E711
        )
    )

    query_data.msg, query_data.emails_selected = await factory.select(query, response, GroupEmailsSelected)

    return query_data