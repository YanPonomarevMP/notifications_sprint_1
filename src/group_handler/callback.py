# type: ignore
"""
Мы знаем, что для корректной работы consume (src/db/message_brokers/rabbit_message_broker.py) нам необходим callback.
В этом модуле мы осуществляем сборку всех написанных сервисов
для работы group_handler в одну функцию-обработчик callback.
"""
import logging
from asyncio import sleep

import orjson
from aio_pika.abc import AbstractIncomingMessage

from config.settings import config
from db.message_brokers.rabbit_message_broker import message_broker_factory
from group_handler.models.message_data import MessageData
from group_handler.services.group_handler import group_handler_service


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
        print('count_retry')
        # logger.info(log_names.error.drop_message, 'Too many repeat inserts in the queue', message_data.x_request_id)
        return await message.ack()

    locked = await group_handler_service.lock(message_data.notification_id)

    # Если не удалось заблокировать, значит уже обработано (или удалено).
    if not locked:
        print('locked or deleted')
        # logger.info(log_names.error.drop_message, 'Message has being processed or deleted', message_data.x_request_id)
        return await message.ack()

    # Начало транзакции.
    try:
        all_users = await group_handler_service.get_data(
            notification_id=message_data.notification_id,
            x_request_id=message_data.x_request_id
        )
        # print(all_users)
        await group_handler_service.post_data(**all_users.dict(), x_request_id=message_data.x_request_id)
        print('всё типа :|')

    except Exception as e:
        # Если не смогли завершить транзакцию, снимаем блокировку и реджектим сообщение.
        print(e)
        await group_handler_service.unlock(message_data.notification_id)
        return await message.reject()


logger = logging.getLogger('group_handler')
