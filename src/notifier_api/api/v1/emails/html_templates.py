"""Модуль содержит CRUD для работы с шаблонами email сообщений"""
from logging import getLogger

from fastapi import APIRouter, Depends, Header

from notifier_api.models.event import EventFromUser
from notifier_api.models.standards_response import BaseNotificationsResponse
# from models.event import EventFromUser
from notifier_api.models.http_responses import http  # type: ignore
from utils.custom_fastapi_router import LoggedRoute
# from models.standards_response import BaseNotificationsResponse
# from services.event_broker import event_broker
from utils.dependencies import authorization_required, requests_per_minute, get_user_id_from_token, new_event

router = APIRouter(
    prefix='/html_templates',
    # tags=['html_templates'],
    # dependencies=[Depends(authorization_required)]
    # dependencies=[Depends(requests_per_minute(3))],
    route_class=LoggedRoute,
)

@router.post(
    '/',
    status_code=http.created.code,
    response_model=BaseNotificationsResponse,
    summary='Records an event',
    description='Endpoint writes a rating to the database',
    response_description='Returns the answer whether the event is recorded in the database',
    dependencies=[Depends(requests_per_minute(10))]
)
async def post_rating(
    rating: EventFromUser,
    authorization: str = Header(default=None, description='12345'),  # noqa: B008
    x_request_log_message: str = Header(default=None, include_in_schema=False),
) -> BaseNotificationsResponse:
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
    answer = {'metadata': http.created}
    # return BaseNotificationsResponse(metadata=http.created)
    return answer


logger = getLogger(__name__)