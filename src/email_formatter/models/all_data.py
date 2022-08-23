from typing import Optional


from email_formatter.models.base_orjson import BaseOrjson


class AllData(BaseOrjson):

    email: Optional[str]
    template: Optional[str]
    message: Optional[dict]
