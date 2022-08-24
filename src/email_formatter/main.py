import asyncio
import logging
from logging import config as logging_config
from typing import Coroutine

import aiohttp
from aio_pika.abc import AbstractIncomingMessage

from config.logging_settings import LOGGING
from config.settings import config
from db.message_brokers.rabbit_message_broker import message_broker_factory
from db.storage import orm_factory
from email_formatter.models.data_from_queue import DataFromQueue
from email_formatter.models.log import log_names
from email_formatter.services.email_formatter import email_formatter_service
from utils import aiohttp_session


async def callback(message: AbstractIncomingMessage) -> None:
    headers = message.info()
    data_from_queue = DataFromQueue(
        x_request_id=headers,
        x_groups=headers,
        notification_id=message.body
    )
    headers = {'X-Request-Id': data_from_queue.x_request_id}
    aiohttp_session.session.headers.update(headers)
    try:
        result = await email_formatter_service.get_data(
            notification_id=data_from_queue.notification_id,
            x_request_id=data_from_queue.x_request_id
        )

        if not email_formatter_service.data_is_valid(result):
            logger.critical(log_names.error.drop_message, f'Already process message or some data is missing ({result})')
            return await message.ack()

        if not email_formatter_service.can_send(result.user_data.groups, data_from_queue.x_groups):
            logger.critical(log_names.error.drop_message, 'User is not subscribed group and message is not urgent')
            return await message.ack()

        result.message.update(result.user_data)
        html_text = await email_formatter_service.render_html(result.template, result.message)

        await email_formatter_service.put_data(
            message_body=html_text,
            queue_name=config.rabbit_mq.queue_formatted_single_messages,
            message_headers=headers
        )
        logger.info(log_names.info.success_completed, f'id message {data_from_queue.notification_id}')
        return await message.ack()

    except Exception as error:
        logger.warning(log_names.warn.retrying, data_from_queue.notification_id, error)
        return await message.reject()


async def startup() -> None:
    headers = {'Authorization': config.auth_api.access_token.get_secret_value()}
    aiohttp_session.session = aiohttp.ClientSession(headers=headers)
    await message_broker_factory.idempotency_startup()
    await orm_factory.db.start()
    logger.info(log_names.info.started, 'formatter handler')


async def shutdown() -> None:
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
logger = logging.getLogger('email_formatter')

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
