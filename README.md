# Code Review № 1

[ссылка на репозиторий с pull request](https://github.com/YanPonomarevMP/notifications_sprint_1/pull/66)

# Проектная работа 10 спринта

https://github.com/YanPonomarevMP/notifications_sprint_1

## Общее описание:
В данном спринте реализован сервис notification.

### Описание архитектуры приложения:
Архитектура всего сервиса в файле: scheme/maybe.puml
* API — FastAPI приложение — интерфейс сервиса (реализовано в src/notifier_api)
* email_sender — хэндлер, отправляющий почту
* email_formatter — хэндлер, форматирующий данные в подходящий для email_sender вид (реализовано в src/email_formatter)
* group_handler — хэндлер, форматирующий групповые рассылки в подходящий для email_formatter вид (реализовано в src/email_sender)
* notifications — реляционная БД (orm можно посмотреть тут src/db/models)
* Rabbit — очередь, с помощью которой сервисы асинхронно общаются друг с другом

Производительность любого узла может быть увеличена запуском ещё одного экземпляра.
Сервис можно легко расширить для отправки других уведомлений, написанием соответствующих хэндлеров.

Конфигурация и безопасность сервиса реализована при помощи Hashicorp Vault

### Rabbit:

Архитектура Rabbit в файле: scheme/architecture_rabbit_mq.puml

При помощи DLXs (Dead letter exchanges) реализовано:

1. Отправка одиночных и групповых сообщений с задержкой (в нужное время)
2. Отправка сообщений каждому пользователю в нужное время в его таймзоне
3. Повтор отправки сообщения в случае неудачи.

### API

адрес документации host/api/openapi

API записывает сообщения в БД и ставит задачи для хэндлеров в Rabbit

API содержит эндпоинты:
1. html_templates — принимает, удаляет (soft delete), возвращает шаблоны сообщений (изменять нельзя — могут быть неотправленные сообщения со старым шаблоном)
2. single_emails — принимает, удаляет (soft delete) и изменяет (если не отправлено), возвращает одиночные сообщения
3. group_emails — принимает, удаляет (soft delete) и изменяет (если не отправлено), возвращает групповые сообщения

Все эндпоинты требуют авторизации (jwt) и защищены rate limit.

Для логирования тела запроса и ответа написаны:
1. Кастомный APIRoute класс для FastAPI (src/utils/custom_fastapi_router.py)
2. Кастомные обработчики исключений для FastAPI (src/utils/custom_exceptions_handlers.py)

Использована асинхронная ORM.

### Хэндлеры (group_handler, email_formatter, email_sender)

Асинхронные consumer/publisher приложения, суть работы которых получать задачу, выполнять обработку и ставить задачу другому хэндлеру.
1. group_handler — получает из Auth список пользователей группы и создаёт для каждого сообщение с учётом его таймзоны.
2. email_formatter — получает из Auth данные пользователя, рендерит шаблон и ставит задачув очередь для отправки.
3. email_sender — отправляет сообщение (проверив на повторную отправку) и записывает в БД результат.
