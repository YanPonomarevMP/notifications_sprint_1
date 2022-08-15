"""Модуль содержит CRUD для работы с шаблонами email сообщений"""
from logging import getLogger

from fastapi import APIRouter, Depends, Header

from notifier_api.models.event import EventFromUser
from notifier_api.models.standards_response import BaseUGCResponse
# from models.event import EventFromUser
from notifier_api.models.http_responses import http  # type: ignore
from utils.custom_fastapi_router import LoggedRoute
# from models.standards_response import BaseUGCResponse
# from services.event_broker import event_broker
from utils.dependencies import authorization_required, requests_per_minute, get_user_id_from_token, new_event

router = APIRouter(
    prefix='/html_templates',
    # tags=['html_templates'],
    # dependencies=[Depends(authorization_required)]
    route_class=LoggedRoute,
)

@router.post(
    '/',
    response_model=BaseUGCResponse,
    summary='Records an event',
    description='Endpoint writes a rating to the database',
    response_description='Returns the answer whether the event is recorded in the database',
    # dependencies=[Depends(requests_per_minute(10))]
)
async def post_rating(
    rating: EventFromUser,
    authorization: str = Header(),  # noqa: B008
) -> BaseUGCResponse:
    """
    Ручка записывает событие в базу данных.

    Args:
        rating: pydantic модель, с распарсиными из body запроса данными, нужными для вставки в БД
        authorization: header Authorization из клиентского запроса (JWT токен клиента)

    Returns:
        Вернёт подтверждение, что операция прошла успешно, или уточнение, что именно пошло не так.
    """
    # user_id = await get_user_id_from_token(authorization)
    # event_data = await new_event(
    #     event=rating,
    #     user_id=user_id,
    #     topic=router.tags[0],
    #     method='create'
    # )
    #
    # await event_broker.put(event_data)
    logger.info('Hello!')
    return BaseUGCResponse(metadata=http.ok)


logger = getLogger(__name__)