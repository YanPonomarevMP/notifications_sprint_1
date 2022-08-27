# type: ignore
"""
Мы знаем, что для корректной работы consume (src/db/message_brokers/rabbit_message_broker.py) нам необходим callback.
В этом модуле мы осуществляем сборку всех написанных сервисов
для работы email_formatter в одну функцию-обработчик callback.
"""
import logging

import orjson
from aio_pika.abc import AbstractIncomingMessage

from config.settings import config
from db.message_brokers.rabbit_message_broker import message_broker_factory
from email_formatter.models.data_from_queue import MessageData
from email_formatter.models.log import log_names
from email_formatter.services.email_formatter import formatter_service


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
    message_data = MessageData(
        x_request_id=header,
        count_retry=header,
        notification_id=message.body
    )

    if message_data.count_retry > config.rabbit_mq.max_retry_count:
        logger.info(log_names.error.drop_message, 'Too many repeat inserts in the queue', message_data.x_request_id)
        return await message.ack()

    locked = await formatter_service.lock(message_data.notification_id)

    # Если не удалось заблокировать, значит уже обработано.
    if not locked:
        logger.info(log_names.error.drop_message, 'Message has being processed or deleted', message_data.x_request_id)
        return await message.ack()

    # Начало транзакции.
    try:
        notification_data = await formatter_service.get_data(
            notification_id=message_data.notification_id,
            x_request_id=message_data.x_request_id
        )

        # Проверяем подписан ли пользователь на сообщение.
        if not formatter_service.check_subscription(notification_data.user_data.groups, notification_data.group):
            logger.info(log_names.error.drop_message, f'User is not subscribed for message', message_data.x_request_id)
            return await message.ack()

        html_text = await formatter_service.render_html(
            template=notification_data.template,
            data=notification_data.message
        )

        formatted_notification = orjson.dumps(
            {
                'html': html_text,
                'to': notification_data.user_data.email,
                'notification_id': message_data.notification_id,
                'reply_to': notification_data.source,
                'subject': notification_data.subject
            }
        )
        await message_broker_factory.publish(
            message_body=formatted_notification,
            queue_name=config.rabbit_mq.queue_formatted_single_messages,
            message_headers={'x-request-id': message_data.x_request_id}
        )
        logger.info(log_names.info.success_completed, f'id {message_data.notification_id}', message_data.x_request_id)
        return await message.ack()  # Только после всех этих действий мы можем сказать очереди — перемога.

    except Exception as error:
        # Если не смогли завершить транзакцию, снимаем блокировку и реджектим сообщение.
        await formatter_service.unlock(message_data.notification_id)
        logger.warning(log_names.warn.retrying, message_data.notification_id, error, message_data.x_request_id)
        return await message.reject()


logger = logging.getLogger('email_formatter')
