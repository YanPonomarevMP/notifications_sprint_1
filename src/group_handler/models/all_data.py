from typing import List, Union, Optional
from uuid import UUID

from group_handler.models.base_config import BaseConfigModel
from group_handler.models.data_single_emails import DataSingleEmails


class AuthData(BaseConfigModel):
    user_id: Optional[UUID]
    hours: Optional[int]
    minutes: Optional[int]


class NotificationData(BaseConfigModel):
    users: List[DataSingleEmails] = []
    send_with_gmt: Optional[bool]


class FinalData(BaseConfigModel):
    users: List[DataSingleEmails]
    send_with_gmt: bool
