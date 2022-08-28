""" Модуль содержит описание сценариев для тестов API"""

from tests.functional.settings import settings
from tests.functional.testdata.models import Scenario


scenarios = [
    # Публикация нового шаблона
    Scenario(
        url='/emails/html_templates/',
        method='POST',
        body={"title": "Заголовок", "template": "<p><strong>Hello {{ name }} {{ surname }} </strong>,</p>"},
        headers={
            'X-Request-Id': settings.const.correct_uuid,
            'Idempotency-Key': settings.const.correct_uuid,
            'Authorization': settings.const.correct_jwt_token
        },
        expected_status=201,
        expected_body={"id": settings.const.correct_uuid, "msg": "Created at 2022-08-28 15:54:26.869732+00:00"},
        check_len_body=True,
        check_len_str_body=True
    ),
    # Публикация нового шаблона повторно (прежний ключ идемпотентности)
    Scenario(
        url='/emails/html_templates/',
        method='POST',
        body={"title": "Заголовок", "template": "<p><strong>Hello {{ name }} {{ surname }} </strong>,</p>"},
        headers={
            'X-Request-Id': settings.const.correct_uuid,
            'Idempotency-Key': settings.const.correct_uuid,
            'Authorization': settings.const.correct_jwt_token
        },
        expected_status=201,
        expected_body={"id": settings.const.correct_uuid, "msg": "Already exist"},
        check_len_body=True,
        check_len_str_body=True
    ),
    # Запрос на получение существующего шаблона по id
    Scenario(
        url=f'/emails/html_templates/{settings.const.correct_uuid}',
        method='GET',
        headers={
            'X-Request-Id': settings.const.correct_uuid,
            'Authorization': settings.const.correct_jwt_token
        },
        expected_status=200,
        expected_body={"msg":"Successfully selected","templates_selected":[{"id":"3aec01aa-3033-4281-964a-5e035e7aac86","title":"Заголовок","template":"<p><strong>Hello {{ name }} {{ surname }} </strong>,</p>"}]},
        check_len_body=True,
        check_len_str_body=True
    ),
    # Запрос на получение шаблона по некорректному id (не валидный UUID)
    Scenario(
        url=f'/emails/html_templates/{settings.const.incorrect_uuid}',
        method='GET',
        headers={
            'X-Request-Id': settings.const.correct_uuid,
            'Authorization': settings.const.correct_jwt_token
        },
        expected_status=422,
        expected_body={"detail":{"loc":["path","template_id"],"msg":"value is not a valid uuid","type":"type_error.uuid"}},
        check_len_body=True,
        check_len_str_body=True,
        check_body=True
    ),
    # Запрос на получение шаблона по НЕ существующему id
    Scenario(
        url=f'/emails/html_templates/{settings.const.not_used_uuid}',
        method='GET',
        headers={
            'X-Request-Id': settings.const.correct_uuid,
            'Authorization': settings.const.correct_jwt_token
        },
        expected_status=404,
        expected_body={"msg":"Not found","templates_selected":[]},
        check_len_body=True,
        check_len_str_body=True,
        check_body=True
    ),
]
# и так далее ... любые тесты с любыми данными за пару минут
