"""Модуль содержит CRUD для работы с шаблонами email сообщений."""
from uuid import UUID

from fastapi import APIRouter, Depends, Header
from fastapi import Response
from sqlalchemy import update, func, and_, select
from sqlalchemy.dialects.postgresql import insert

from db.models.email_templates import HTMLTemplates
from notifier_api.models.http_responses import http  # type: ignore
from notifier_api.models.notifier_html_template import HtmlTemplatesResponse, HtmlTemplatesRequest,\
    HtmlTemplatesQuery, HtmlTemplatesResponseSelected, HtmlTemplateSelected
from notifier_api.services.emails_factory import get_emails_factory, EmailsFactory
from utils.custom_fastapi_router import LoggedRoute
from utils.dependencies import requests_per_minute

router = APIRouter(
    prefix='/html_templates',
    route_class=LoggedRoute,
)


@router.post(
    path='/',
    status_code=http.created.code,
    response_model=HtmlTemplatesResponse,
    summary='Create new template',
    description='Endpoint writes new template into database',
    response_description='Returns the answer whether the template is recorded in the database',
    dependencies=[Depends(requests_per_minute(3))]
)
async def new_template(
    template: HtmlTemplatesRequest,
    factory: EmailsFactory = Depends(get_emails_factory),
    idempotency_key: UUID = Header(description='UUID4'),
) -> HtmlTemplatesResponse:
    """
    Метод создаёт новый шаблон.

    Args:
        template: данные для шаблона
        factory: обработчик
        idempotency_key: ключ идемпотентности

    Returns:
        Сообщение об изменении сообщения или об ошибке.
    """
    query_data = HtmlTemplatesQuery(**template.dict())
    query_data.id = idempotency_key

    query = insert(HTMLTemplates)
    query = query.returning(HTMLTemplates.created_at)
    query = query.values(**query_data.dict(exclude={'msg', 'templates_selected'}))
    idempotent_query = query.on_conflict_do_nothing(index_elements=['id'])

    query_data.msg = await factory.insert(idempotent_query)

    return query_data


@router.delete(
    path='/{template_id}',
    status_code=http.ok.code,
    response_model=HtmlTemplatesResponse,
    summary='Delete template',
    description='Endpoint delete template from database',
    response_description='Returns the answer whether the template is deleted from the database',
    dependencies=[Depends(requests_per_minute(3))]
)
async def delete_template(
    template_id: UUID,
    response: Response,
    factory: EmailsFactory = Depends(get_emails_factory),
) -> HtmlTemplatesResponse:
    """
    Ручка удаляет шаблон по его id.

    Args:
        template_id: id шаблона
        response: класс Response нужен для изменения статус кода при ошибке
        factory: обработчик

    Returns:
        Сообщение об изменении сообщения или об ошибке.
    """
    query_data = HtmlTemplatesQuery(id=template_id)

    query = update(HTMLTemplates)
    query = query.returning(HTMLTemplates.deleted_at)
    query = query.filter(
        and_(
            HTMLTemplates.id == query_data.id,
            HTMLTemplates.deleted_at == None  # noqa: E711
        )
    )
    query = query.values(deleted_at=func.now())

    query_data.msg = await factory.delete(query, response)

    return query_data


@router.get(
    path='/{template_id}',
    status_code=http.ok.code,
    response_model=HtmlTemplatesResponseSelected,
    summary='Get one template',
    description='Endpoint returns template data from database',
    response_description='Template data',
    dependencies=[Depends(requests_per_minute(3))]
)
async def get_template(
    template_id: UUID,
    response: Response,
    factory: EmailsFactory = Depends(get_emails_factory),
) -> HtmlTemplatesResponse:
    """
    Ручка достаёт шаблон по его id.

    Args:
        template_id: id шаблона
        response: класс Response нужен для изменения статус кода при ошибке
        factory: обработчик

    Returns:
        Вернёт шаблон или ошибку.
    """
    query_data = HtmlTemplatesQuery(id=template_id)

    query = select(
        HTMLTemplates.id,
        HTMLTemplates.title,
        HTMLTemplates.template
    )
    query = query.filter(
        and_(
            HTMLTemplates.id == query_data.id,
            HTMLTemplates.deleted_at == None  # noqa: E711
        )
    )

    query_data.msg, query_data.templates_selected = await factory.select(query, response, HtmlTemplateSelected)

    return query_data


@router.get(
    path='/',
    status_code=http.ok.code,
    response_model=HtmlTemplatesResponseSelected,
    summary='Get all templates',
    description='Endpoint returns all templates data from database',
    response_description='Templates data',
    dependencies=[Depends(requests_per_minute(3))]
)
async def get_all_templates(
    response: Response,
    factory: EmailsFactory = Depends(get_emails_factory),
) -> HtmlTemplatesResponse:
    """
    Ручка достаёт все шаблоны.

    Args:
        response: класс Response нужен для изменения статус кода при ошибке
        factory: обработчик

    Returns:
        Вернёт все шаблоны или ошибку.
    """
    query_data = HtmlTemplatesQuery()

    query = select(
        HTMLTemplates.id,
        HTMLTemplates.title,
        HTMLTemplates.template
    )
    query = query.filter(
        and_(
            HTMLTemplates.deleted_at == None  # noqa: E711
        )
    )

    query_data.msg, query_data.templates_selected = await factory.select(query, response, HtmlTemplateSelected)

    return query_data
