# type: ignore
"""
Модуль содержит основную логику работы сервиса.

Мы знаем, что для корректной работы consume (src/db/message_brokers/rabbit_message_broker.py) нам необходим callback.
В этом модуле мы осуществляем сборку всех написанных сервисов
для работы email_formatter в одну функцию-обработчик callback и запускаем consume с этим обработчиком.

Стоит пояснить что вообще делает email_formatter:

Его задача принимать сообщение из одной очереди, форматировать (рендерить HTML шаблон) и отправлять в другую очередь.
Помимо самого HTML он еще должен найти адресата (его почту) в Auth сервисе и тоже отправить в очередь.
"""
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
from email_formatter.services.email_formatter import formatter_service
from utils import aiohttp_session


async def callback(message: AbstractIncomingMessage) -> None:  # noqa: WPS231,WPS212,WPS213
    """
    Функция-обработчик сообщений.

    Когда consumer очереди выловит очередное сообщение — оно попадёт в эту функцию.
    Тут мы будем обрабатывать сообщение исходя из нашей бизнес логики механизмом, очень напоминающем транзакцию.

    Ниже по коду я четко расписала каждое важное действие,
    что бы было видно, в каких случаях чего мы делаем с сообщением.

    PS:
    Если вы не знаете что такое message.ack(), message.reject(), которые присутствуют в коде —
    советую посмотреть на эту статью https://www.rabbitmq.com/confirms.html#acknowledgement-modes
    Там подробно описано что это такое и зачем.

    Args:
        message: сообщение, приходящее из очереди
    """
    header = message.info()
    message_data = DataFromQueue(
        x_request_id=header,
        count_retry=header,
        notification_id=message.body
    )

    if message_data.count_retry > config.rabbit_mq.max_retry_count:
        logger.info(log_names.error.drop_message, 'Too many repeat inserts in the queue')
        return await message.ack()

    locked = await formatter_service.lock(message_data.notification_id)

    # Если не удалось заблокировать, значит уже обработано.
    if not locked:
        logger.info(log_names.error.drop_message, 'Message has being processed by someone')
        return await message.ack()

    # Начало транзакции.
    try:
        notification_data = await formatter_service.get_data(
            notification_id=message_data.notification_id,
            x_request_id=message_data.x_request_id
        )

        # Проверяем подписан ли пользователь на сообщение.
        if not formatter_service.check_subscription(notification_data.user_data.groups, notification_data.group):
            logger.info(log_names.error.drop_message, 'User is not subscribed for this message')
            return await message.ack()

        html_text = await formatter_service.render_html(
            template=notification_data.template,
            data=notification_data.message
        )

        formatted_notification = orjson.dumps(
            {
                'html': html_text,
                'email': notification_data.user_data.email,
                'notification_id': message_data.notification_id,
                'source': notification_data.source,
                'subject': notification_data.subject
            }
        )
        await message_broker_factory.publish(
            message_body=formatted_notification,
            queue_name=config.rabbit_mq.queue_formatted_single_messages,
            message_headers=header
        )
        logger.info(log_names.info.success_completed, f'id message {message_data.notification_id}')
        return await message.ack()  # Только после всех этих действий мы можем сказать очереди — перемога.

    except Exception as error:
        # Если не смогли завершить транзакцию, снимаем блокировку и реджектим сообщение.
        await formatter_service.unlock(message_data.notification_id)
        logger.warning(log_names.warn.retrying, message_data.notification_id, error)
        return await message.reject()


async def startup() -> None:

    """Функция для действий во время старта приложения."""

    headers = {'Authorization': config.auth_api.access_token.get_secret_value()}
    aiohttp_session.session = aiohttp.ClientSession(headers=headers)
    await message_broker_factory.idempotency_startup()
    await orm_factory.db.start()
    logger.info(log_names.info.started, 'formatter handler')


async def shutdown() -> None:

    """Функция для действий во время завершения работы приложения."""

    await aiohttp_session.session.close()
    await orm_factory.db.stop()


async def main() -> None:

    """Функция, запускающая всё приложение."""

    await startup()
    await message_broker_factory.consume(
        queue_name=config.rabbit_mq.queue_raw_single_messages,
        callback=callback
    )
    await shutdown()


logging_config.dictConfig(LOGGING)
logger = logging.getLogger('email_formatter')

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
