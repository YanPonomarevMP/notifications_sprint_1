"""Модуль содержит основную логику работы сервиса."""
import asyncio
import logging
from logging import config as logging_config

import aiohttp
import orjson
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
    transaction = await email_formatter_service.start_transaction(data_from_queue.notification_id)

    if not transaction:
        logger.critical(log_names.error.drop_message, f'Message is already being processed by someone')
        return await message.ack()

    try:
        data_from_service = await email_formatter_service.get_data(
            notification_id=data_from_queue.notification_id,
            x_request_id=data_from_queue.x_request_id
        )

        if not email_formatter_service.data_is_valid(data_from_service):
            logger.critical(log_names.error.drop_message, f'Some data is missing ({data_from_service})')
            return await message.ack()

        if not email_formatter_service.groups_match(data_from_service.user_data.groups, data_from_queue.x_groups):
            logger.critical(log_names.error.drop_message, 'User is not subscribed group and message is not urgent')
            return await message.ack()

        data_from_service.message.update(data_from_service.user_data)
        html_text = await email_formatter_service.render_html(data_from_service.template, data_from_service.message)

        data_for_queue = orjson.dumps(
            {
                'html': html_text,
                'email': data_from_service.user_data.email,
                'notification_id': data_from_queue.notification_id
            }
        )
        await email_formatter_service.put_data(
            message_body=data_for_queue,
            queue_name=config.rabbit_mq.queue_formatted_single_messages,
            message_headers=headers
        )
        logger.info(log_names.info.success_completed, f'id message {data_from_queue.notification_id}')
        return await message.ack()

    except Exception as error:
        await email_formatter_service.abort_transaction(data_from_queue.notification_id)
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
