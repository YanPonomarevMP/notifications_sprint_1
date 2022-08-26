import asyncio
import logging
from logging import config as logging_config

from aio_pika.abc import AbstractIncomingMessage

from config.logging_settings import LOGGING
from config.settings import config
from db.message_brokers.rabbit_message_broker import message_broker_factory
from db.storage import orm_factory
from email_sender.models.log import log_names
from email_sender.models.message_data import MessageData
from email_sender.services.email_sender import sender_service


async def callback(message: AbstractIncomingMessage):
    header = message.info()
    message_data = MessageData(
        x_request_id=header,
        count_retry=header,
        notification_id=message.body,
        html=message.body,
        reply_to=message.body,
        to=message.body,
        subject=message.body
    )
    if message_data.count_retry > config.rabbit_mq.max_retry_count:
        logger.info(log_names.error.drop_message, 'Too many repeat inserts in the queue')
        return await message.ack()

    locked = await sender_service.lock(message_data.notification_id)

    # Если не удалось заблокировать, значит уже обработано (или удалено).
    if not locked:
        logger.info(log_names.error.drop_message, 'Message has being processed by someone or deleted')
        return await message.ack()

    try:
        notification = sender_service.create_notification(message_data)
        smtp_response = await sender_service.post_notification(notification)
        await sender_service.post_response(notification_id=message_data.notification_id, response=smtp_response)
        logger.info(log_names.info.success_data_sent, message_data.notification_id)
        return await message.ack()

    except Exception as error:
        logger.warning(log_names.warn.retrying, message_data.notification_id, error)
        await sender_service.unlock(message_data.notification_id)
        return await message.reject()


async def startup() -> None:

    """Функция для действий во время старта приложения."""

    await message_broker_factory.idempotency_startup()
    await orm_factory.db.start()
    logger.info(log_names.info.started, 'email sender')


async def shutdown() -> None:

    """Функция для действий во время завершения работы приложения."""

    await orm_factory.db.stop()


async def main() -> None:

    """Функция, запускающая всё приложение."""

    await startup()
    await message_broker_factory.consume(
        queue_name=config.rabbit_mq.queue_formatted_single_messages,
        callback=callback
    )
    await shutdown()


logging_config.dictConfig(LOGGING)
logger = logging.getLogger('email_sender')

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
