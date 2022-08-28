"""Модуль содержит CRUD для работы с групповыми email сообщениями."""
from uuid import UUID

from fastapi import APIRouter, Depends, Header
from fastapi import Response
from sqlalchemy import update, func, and_, select
from sqlalchemy.dialects.postgresql import insert

from config.settings import config
from db.models.email_group_notifications import GroupEmails
from notifier_api.models.http_responses import http  # type: ignore
from notifier_api.models.message_broker_models import MessageBrokerData
from notifier_api.models.notifier_group_emails import GroupEmailsResponse, GroupEmailsRequest, GroupEmailsQuery, \
    GroupEmailsResponseSelected, GroupEmailsRequestUpdate, GroupEmailsSelected
from notifier_api.services.emails_factory import get_emails_factory, EmailsFactory
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
    group_email: GroupEmailsRequest,
    factory: EmailsFactory = Depends(get_emails_factory),  # noqa: B008
    idempotency_key: UUID = Header(description='UUID4'),  # noqa: B008
    x_request_id: str = Header(),  # noqa: B008, WPS204
) -> GroupEmailsResponse:
    """
    Ручка принимает новый групповой email (рассылку) для отправки.

    Args:
        group_email: тело запроса
        factory: обработчик запросов
        idempotency_key: ключ идемпотентности
        x_request_id: id запроса

    Returns:
        Сообщение id принятого email или сообщение об ошибке.
        В случае повтора запроса вернёт код успеха и msg: Already exist
    """

    query_data = GroupEmailsQuery(**group_email.dict())
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
    group_email: GroupEmailsRequestUpdate,
    response: Response,
    factory: EmailsFactory = Depends(get_emails_factory),  # noqa: B008
) -> GroupEmailsResponse:
    """
    Ручка изменяет сообщение (возможно в течении delay периода).

    Args:
        group_email: тело запроса
        response: класс Response нужен для изменения статус кода при ошибке
        factory: обработчик

    Returns:
        Сообщение об изменении сообщения или об ошибке.
    """

    query_data = GroupEmailsQuery(**group_email.dict())

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
    factory: EmailsFactory = Depends(get_emails_factory),  # noqa: B008
) -> GroupEmailsResponse:
    """
    Ручка удаляет email (возможно в течении delay периода).
    Выполняется мягкое удаление, ставится отметка deleted_at.

    Args:
        email_id: id удаляемого email
        response: класс Response нужен для изменения статус кода при ошибке
        factory: обработчик запроса

    Returns:
        Сообщение об удалении сообщения или об ошибке.
    """

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
    factory: EmailsFactory = Depends(get_emails_factory),  # noqa: B008
) -> GroupEmailsResponse:
    """
    Ручка возвращает данные конкретного сообщения по id.

    Args:
        email_id: id сообщения
        response: класс Response нужен для изменения статус кода при ошибке
        factory: обработчик

    Returns:
        JSON с данными сообщения или ошибку.
    """

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
