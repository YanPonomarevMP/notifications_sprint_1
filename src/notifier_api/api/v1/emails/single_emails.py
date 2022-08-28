"""Модуль содержит CRUD для работы с шаблонами email сообщений."""
from uuid import UUID

from fastapi import APIRouter, Depends, Header
from fastapi import Response
from sqlalchemy import update, func, and_, select
from sqlalchemy.dialects.postgresql import insert

from config.settings import config
from db.models.email_single_notifications import SingleEmails
from notifier_api.models.http_responses import http  # type: ignore
from notifier_api.models.message_broker_models import MessageBrokerData
from notifier_api.models.notifier_single_emails import SingleEmailsResponse, SingleEmailsRequest, SingleEmailsQuery, \
    SingleEmailsResponseSelected, SingleEmailsRequestUpdate, SingleEmailsSelected
from notifier_api.services.emails_factory import get_emails_factory, EmailsFactory
from utils.custom_fastapi_router import LoggedRoute
from utils.dependencies import requests_per_minute

router = APIRouter(
    prefix='/single_emails',
    route_class=LoggedRoute,
)


@router.post(
    path='/',
    status_code=http.accepted.code,
    response_model=SingleEmailsResponse,
    summary='Create new email',
    description='Endpoint accepts email for processing',
    response_description='Returns the answer whether the email accepted but not sent yet',
    dependencies=[Depends(requests_per_minute(3))]
)
async def new_email(
    single_email: SingleEmailsRequest,
    factory: EmailsFactory = Depends(get_emails_factory),
    idempotency_key: UUID = Header(description='UUID4'),
    x_request_id: str = Header(),  # noqa: WPS204
) -> SingleEmailsResponse:
    """
    Ручка создаёт новую почту.

    Args:
        single_email: данные
        factory: обработчик запроса
        idempotency_key: ключ идемпотентности
        x_request_id: id запроса

    Returns:
        Сообщение об вставке сообщения или об ошибке.
    """
    query_data = SingleEmailsQuery(**single_email.dict())
    query_data.id = idempotency_key

    query = insert(SingleEmails)
    query = query.returning(SingleEmails.created_at)
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
    response_model=SingleEmailsResponse,
    summary='Create new email',
    description='Endpoint accepts email for processing',
    response_description='Returns the answer whether the email accepted but not sent yet',
    dependencies=[Depends(requests_per_minute(3))]
)
async def update_email(
    single_email: SingleEmailsRequestUpdate,
    response: Response,
    factory: EmailsFactory = Depends(get_emails_factory),
) -> SingleEmailsResponse:
    """
    Ручка обновляет почту.

    Args:
        single_email: данные почты
        response: класс Response нужен для изменения статус кода при ошибке
        factory: обработчик запроса

    Returns:
        Сообщение об обновлении сообщения или об ошибке.
    """
    query_data = SingleEmailsQuery(**single_email.dict())

    query = update(SingleEmails)
    query = query.returning(SingleEmails.created_at)
    query = query.filter(
        and_(
            SingleEmails.id == query_data.id,
            SingleEmails.deleted_at == None,  # noqa: E711
            SingleEmails.passed_to_handler_at == None  # noqa: E711
        )
    )
    query = query.values(**query_data.dict(exclude={'msg', 'emails_selected', 'id'}))

    query_data.msg = await factory.update(query, response)

    return query_data


@router.delete(
    path='/{email_id}',
    status_code=http.ok.code,
    response_model=SingleEmailsResponse,
    summary='Delete email',
    description='Endpoint delete email from database before send',
    response_description='Returns the answer whether the email is deleted',
    dependencies=[Depends(requests_per_minute(3))]
)
async def delete_email(
    email_id: UUID,
    response: Response,
    factory: EmailsFactory = Depends(get_emails_factory),
) -> SingleEmailsResponse:
    """
    Ручка удаляет почту по Id.

    Args:
        email_id: id почты
        response: класс Response нужен для изменения статус кода при ошибке
        factory: обработчик

    Returns:
        Сообщение об удалении или об ошибке.
    """
    query_data = SingleEmailsQuery(id=email_id)

    query = update(SingleEmails)
    query = query.returning(SingleEmails.deleted_at)
    query = query.filter(
        and_(
            SingleEmails.id == query_data.id,
            SingleEmails.deleted_at == None,  # noqa: E711
            SingleEmails.passed_to_handler_at == None  # noqa: E711
        )
    )
    query = query.values(deleted_at=func.now())

    query_data.msg = await factory.delete(query, response)

    return query_data


@router.get(
    path='/{email_id}',
    status_code=http.ok.code,
    response_model=SingleEmailsResponseSelected,
    summary='Get one email',
    description='Endpoint returns email data from database',
    response_description='Email data',
    dependencies=[Depends(requests_per_minute(3))]
)
async def get_email(
    email_id: UUID,
    response: Response,
    factory: EmailsFactory = Depends(get_emails_factory),
) -> SingleEmailsResponse:
    """
    Ручка достаёт почту по id.

    Args:
        email_id: id почты
        response: класс Response нужен для изменения статус кода при ошибке
        factory:обработчик

    Returns:
        JSON с данными сообщения или ошибку.
    """
    query_data = SingleEmailsQuery(id=email_id)

    query = select(
        SingleEmails.id,
        SingleEmails.source,
        SingleEmails.destination_id,
        SingleEmails.template_id,
        SingleEmails.subject,
        SingleEmails.message,
        SingleEmails.delay
    )
    query = query.filter(
        and_(
            SingleEmails.id == query_data.id,
            SingleEmails.deleted_at == None  # noqa: E711
        )
    )

    query_data.msg, query_data.emails_selected = await factory.select(query, response, SingleEmailsSelected)

    return query_data
