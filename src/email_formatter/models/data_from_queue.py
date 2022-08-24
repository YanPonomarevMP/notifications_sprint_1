from typing import Union, Optional
from uuid import UUID

from pydantic import validator

from email_formatter.models.base_config import BaseConfigModel


class DataFromQueue(BaseConfigModel):

    x_request_id: Union[str, dict]
    x_groups: Optional[Union[dict, list]]
    notification_id: Union[bytes, str]

    @validator('x_request_id')
    def dict_to_str(cls, message: dict) -> str:
        return message['headers']['x-request-id']

    @validator('x_groups')
    def dict_to_list(cls, message: dict) -> Optional[list]:
        return message['headers'].get('x-groups', None)

    @validator('notification_id')
    def byte_to_str(cls, message: bytes) -> str:
        return message.decode()
