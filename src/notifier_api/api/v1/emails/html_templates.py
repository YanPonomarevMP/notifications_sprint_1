"""Модуль содержит CRUD для работы с шаблонами email сообщений"""
from logging import getLogger

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.dialects.postgresql import insert

from db.models.email_templates import HTMLTemplates
from db.storage.orm_factory import get_db, AsyncPGClient
from notifier_api.models.http_responses import http  # type: ignore
from notifier_api.models.notifier_html_template import HtmlTemplatesResponse, HtmlTemplatesRequest, HtmlTemplatesQuery
from notifier_api.services.html_templates_factory import get_html_templates_factory
from utils.custom_exceptions import DataBaseError
from utils.custom_fastapi_router import LoggedRoute
from utils.dependencies import requests_per_minute

router = APIRouter(
    prefix='/html_templates',
    route_class=LoggedRoute,
)


@router.post(
    '/',
    status_code=http.created.code,
    response_model=HtmlTemplatesResponse,
    summary='Create new template',
    description='Endpoint writes new template into database',
    response_description='Returns the answer whether the template is recorded in the database',
    dependencies=[Depends(requests_per_minute(3))]
)
async def new_template(
    template: HtmlTemplatesRequest,
    factory: AsyncPGClient = Depends(get_html_templates_factory),
    idempotency_key: str = Header(description='UUID4'),  # noqa: B008
) -> HtmlTemplatesResponse:

    query_data = HtmlTemplatesQuery(**template.dict())
    query_data.id = idempotency_key

    query = insert(HTMLTemplates)
    query = query.returning(HTMLTemplates.created_at)
    query = query.values(**query_data.dict(exclude={'msg'}))
    idempotent_query = query.on_conflict_do_nothing(index_elements=['id'])

    query_data.msg = await factory.execute(idempotent_query)

    return query_data
