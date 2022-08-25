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
from email_formatter.services.email_formatter import email_formatter_service
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
    headers = message.info()
    data_from_queue = DataFromQueue(
        x_request_id=headers,
        x_groups=headers,
        count_retry=headers,
        notification_id=message.body
    )

    # Сообщение больше допустимого повторно встаёт в очередь после reject.
    if data_from_queue.count_retry > config.rabbit_mq.max_retry_count:
        logger.critical(log_names.error.drop_message, 'Too many repeat inserts in the queue')
        return await message.ack()

    transaction = await email_formatter_service.start_transaction(data_from_queue.notification_id)

    # Сообщение уже кем-то взято, значит это сообщение досталось нам по ошибке и обрабатывать его не надо.
    if not transaction:
        logger.critical(log_names.error.drop_message, 'Message is already being processed by someone')
        return await message.ack()

    # Началась обработка сообщения. Если в процессе блока try мы получим исключение — сообщение не пропадёт.
    try:
        data_from_service = await email_formatter_service.get_data(
            notification_id=data_from_queue.notification_id,
            x_request_id=data_from_queue.x_request_id
        )
        if not email_formatter_service.can_send(data_from_service, data_from_queue):
            return await message.ack()  # Если мы не можем продолжить — дропим сообщение.

        data_from_service.message.update(data_from_service.user_data)
        html_text = await email_formatter_service.render_html(
            template=data_from_service.template,
            data=data_from_service.message
        )

        data_for_queue = orjson.dumps(
            {
                'html': html_text,
                'email': data_from_service.user_data.email,
                'notification_id': data_from_queue.notification_id
            }
        )
        await message_broker_factory.publish(
            message_body=data_for_queue,
            queue_name=config.rabbit_mq.queue_formatted_single_messages,
            message_headers=headers
        )
        logger.info(log_names.info.success_completed, f'id message {data_from_queue.notification_id}')
        return await message.ack()  # Только после всех этих действий мы можем сказать очереди — перемога.

    except Exception as error:
        # По какой-то причине мы не смогли корректно завершить обработку (к примеру Auth обвалился).
        # Это означает, что сообщение пойдёт в «спячку» на некоторое время и транзакцию мы принудительно прерываем.
        await email_formatter_service.abort_transaction(data_from_queue.notification_id)
        logger.warning(log_names.warn.retrying, data_from_queue.notification_id, error)
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
