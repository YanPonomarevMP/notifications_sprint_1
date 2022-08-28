from typing import Dict, Optional
from uuid import UUID

from group_handler.models.base_config import BaseConfigModel


class DataSingleEmails(BaseConfigModel):

    """Данные, поступившие от клиента."""

    source: str
    destination_id: UUID
    template_id: UUID
    group_id: Optional[UUID]
    subject: str
    message: Dict
    delay: int = 0
    send_with_gmt: bool = False
