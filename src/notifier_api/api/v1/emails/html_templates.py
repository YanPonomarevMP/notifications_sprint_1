"""Модуль содержит CRUD для работы с шаблонами email сообщений"""
from logging import getLogger

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.dialects.postgresql import insert

from db.models.email_templates import HTMLTemplates
from db.storage.orm_factory import get_db, AsyncPGClient
from notifier_api.models.http_responses import http  # type: ignore
from notifier_api.models.notifier_html_template import HtmlTemplatesResponse, HtmlTemplatesRequest, HtmlTemplatesQuery
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
    database: AsyncPGClient = Depends(get_db),
    idempotency_key: str = Header(description='UUID4'),  # noqa: B008
    x_request_logger_name: str = Header(include_in_schema=False)
) -> HtmlTemplatesResponse:

    query_data = HtmlTemplatesQuery(**template.dict())
    query_data.id = idempotency_key

    query = insert(HTMLTemplates).returning(HTMLTemplates.created_at).values(**query_data.dict(exclude={'msg'}))
    idempotent_query = query.on_conflict_do_nothing(index_elements=['id'])

    try:
        query_data.msg = await database.execute(idempotent_query)
    except DataBaseError as error:
        logger = getLogger(x_request_logger_name)
        logger.critical(error.message)
        raise HTTPException(status_code=http.backoff_error.code, detail=http.backoff_error.message)

    return query_data
