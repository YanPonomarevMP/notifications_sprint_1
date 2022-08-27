from typing import Dict, Optional, Union

from notifier_api.models.base_orjson import BaseOrjson


class MessageBrokerData(BaseOrjson):

    """Данные для загрузки в брокер сообщений."""

    message_body: bytes
    queue_name: str
    message_headers: Optional[Dict]
    delay: Union[int, float] = 0