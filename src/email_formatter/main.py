import asyncio
from uuid import UUID
from logging import config as logging_config

from config.logging_settings import LOGGING
# from db.storage import orm_factory
from db.storage.orm_factory import AsyncPGClient
from email_formatter.services.email_formatter import email_formatter_service


async def main():
    result = await email_formatter_service.get_data(UUID('8aeb94b9-5f1d-42bf-8beb-54a045440474'))
    print(result)


logging_config.dictConfig(LOGGING)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
