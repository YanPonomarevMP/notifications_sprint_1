import asyncio

# from db.storage import orm_factory
from db.storage.orm_factory import AsyncPGClient
# from email_formatter.services.email_formatter import email_formatter_service


async def main():
    db = AsyncPGClient()
    await db.start()
    print('12345654321')
    # message, template = await email_formatter_service.get_data('8aeb94b9-5f1d-42bf-8beb-54a045440474')
    # print(message, template)
    # await orm_factory.db.stop()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
