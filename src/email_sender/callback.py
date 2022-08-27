# type: ignore
"""
Мы знаем, что для корректной работы consume (src/db/message_brokers/rabbit_message_broker.py) нам необходим callback.
В этом модуле мы осуществляем сборку всех написанных сервисов
для работы email_sender в одну функцию-обработчик callback.
"""
import logging

from aio_pika.abc import AbstractIncomingMessage

from config.settings import config
from email_sender.models.log import log_names
from email_sender.models.message_data import MessageData
from email_sender.services.email_sender import sender_service


async def callback(message: AbstractIncomingMessage) -> None:
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
        notification_id=message.body,
        html=message.body,
        reply_to=message.body,
        to=message.body,
        subject=message.body
    )
    if message_data.count_retry > config.rabbit_mq.max_retry_count:
        content = f'Too many repeat inserts in the queue. X-Request-Id {message_data.x_request_id}'
        logger.info(log_names.error.drop_message, content)
        return await message.ack()

    locked = await sender_service.lock(message_data.notification_id)

    # Если не удалось заблокировать, значит уже обработано (или удалено).
    if not locked:
        content = f'Message has being processed by someone or deleted. X-Request-Id {message_data.x_request_id}'
        logger.info(log_names.error.drop_message, content)
        return await message.ack()

    # Начало транзакции.
    try:
        notification = sender_service.create_notification(message_data)
        smtp_response = await sender_service.post_notification(notification)
        await sender_service.post_response(message_data.notification_id, smtp_response)

        content = f'id {message_data.notification_id}. X-Request-Id {message_data.x_request_id}'
        logger.info(log_names.info.success_data_sent, content)
        return await message.ack()  # Говорим — перемога!

    except Exception as error:
        # Если не смогли завершить транзакцию, снимаем блокировку и реджектим сообщение.
        logger.warning(log_names.warn.retrying, message_data.notification_id, error, message_data.x_request_id)
        await sender_service.unlock(message_data.notification_id)
        return await message.reject()


logger = logging.getLogger('email_sender')
