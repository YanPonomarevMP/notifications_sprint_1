import asyncio
from logging import config as logging_config

import aiohttp
from aio_pika.abc import AbstractIncomingMessage

from config.logging_settings import LOGGING
from config.settings import config
from db.message_brokers.rabbit_message_broker import message_broker_factory
from email_formatter.models.data_from_queue import DataFromQueue
from email_formatter.services.email_formatter import email_formatter_service
from utils import aiohttp_session


async def callback(message: AbstractIncomingMessage):
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

        if not email_formatter_service.data_is_valid(result):
            return await message.ack()  # Сообщение уже кто-то обрабатывает или каких-то данных не хватает.

        if not email_formatter_service.can_send(result.user_data.groups, data_from_queue.x_groups):
            return await message.ack()  # Пользователь не подписан на группу и это сообщение не экстренное

        result.message.update(result.user_data)
        html_text = await email_formatter_service.render_html(result.template, result.message)

        await email_formatter_service.put_data(
            message_body=html_text,
            queue_name=config.rabbit_mq.queue_formatted_single_messages,
            message_headers=headers
        )

    except Exception:
        return await message.reject()


async def main():
    aiohttp_session.session = aiohttp.ClientSession()
    headers = {'Authorization': config.auth_api.access_token.get_secret_value()}
    aiohttp_session.session = aiohttp.ClientSession(headers=headers)

    await message_broker_factory.consume(
        queue_name=config.rabbit_mq.queue_raw_single_messages,
        callback=callback
    )
    await aiohttp_session.session.close()
    # result = await email_formatter_service.get_data(
    #     UUID('8aeb94b9-5f1d-42bf-8beb-54a045440474'),
    #     '124567',
    #     # config.auth_api.access_token
    # )
    #
    # if result is None:
    #     print('Уже было кем-то взято в обработку.')
    #     return
    # if await email_formatter_service.data_is_valid(result):
    #     print('Есть все данные')
    # # a = await email_formatter_service.render_html(result.template, result.user_data.dict())
    # print(result)


logging_config.dictConfig(LOGGING)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
