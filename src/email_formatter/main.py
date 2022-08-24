import asyncio
from logging import config as logging_config

import aiohttp
from aio_pika.abc import AbstractIncomingMessage

from config.logging_settings import LOGGING
from config.settings import config
from db.message_brokers.rabbit_message_broker import message_broker_factory
from db.storage import orm_factory
from email_formatter.models.data_from_queue import DataFromQueue
from email_formatter.services.email_formatter import email_formatter_service
from utils import aiohttp_session


async def callback(message: AbstractIncomingMessage):
    print()
    print('мы взяли ваше сообщение')
    headers = message.info()
    data_from_queue = DataFromQueue(
        x_request_id=headers,
        x_groups=headers,
        notification_id=message.body
    )
    try:
        result = await email_formatter_service.get_data(
            notification_id=data_from_queue.notification_id,
            x_request_id=data_from_queue.x_request_id
        )

        print('взяли все данные')

        if not email_formatter_service.data_is_valid(result):
            print('не все данные, или кто-то уже взял')
            return await message.ack()  # Сообщение уже кто-то обрабатывает или каких-то данных не хватает.

        if not email_formatter_service.can_send(result.user_data.groups, data_from_queue.x_groups):
            print('у пользователя есть нужные группы, или сообщение срочное')
            return await message.ack()  # Пользователь не подписан на группу и при этом сообщение не экстренное

        print('все тесты на вшивость прошли, переходим к рендеру шаблона')
        result.message.update(result.user_data)
        html_text = await email_formatter_service.render_html(result.template, result.message)

        await email_formatter_service.put_data(
            message_body=html_text,
            queue_name=config.rabbit_mq.queue_formatted_single_messages,
            message_headers=headers
        )
        print('мы всё записали')
        return await message.ack()

    except Exception as e:
        print('что-то пошло не так', e)
        return await message.reject()


async def startup():
    headers = {'Authorization': config.auth_api.access_token.get_secret_value()}
    aiohttp_session.session = aiohttp.ClientSession(headers=headers)
    await message_broker_factory.idempotency_startup()
    await orm_factory.db.start()
    print('случаю вас очень внимательно')


async def shutdown():
    print('закончил слушать')
    await aiohttp_session.session.close()
    await orm_factory.db.stop()


async def main():

    await startup()
    await message_broker_factory.consume(
        queue_name=config.rabbit_mq.queue_raw_single_messages,
        callback=callback
    )
    await shutdown()


logging_config.dictConfig(LOGGING)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
