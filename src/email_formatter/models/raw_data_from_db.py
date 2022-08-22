from typing import Union
from uuid import UUID

import orjson
from pydantic import validator

from email_formatter.models.base_orjson import BaseOrjson


class RawData(BaseOrjson):
    template_id: UUID
    destination_id: UUID
    message: Union[dict, str]

    @validator('message')
    def json_to_dict(cls, message: str):
        return orjson.loads(message)
