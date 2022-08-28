""" Модуль содержит описание сценариев для тестов API"""
import uuid

from pydantic import create_model

from tests.functional.testdata.models import Scenario

# Список страшный на вид, но простой по сути.
#
# Он содержит пары:
# <ключ> — запрос к API:
# <значение> — параметры запросы и ожидаемый ответ API в виде словаря {'status': int, 'body': json}
#
# Для добавления нового теста нужно:
# 1. добавить новую строку (внизу есть пример)
# 2. в качестве ключа указать запрос к API в виде строки, начиная со '/'
# 3. Записать в ключ status статус ответа API
# 4. скопировать ответ API в ключ 'body'
# словарь удобнее читать/править построчно, а не форматировать в иерархическую структуру
correct_jwt_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY1NDAwNzE5NiwianRpIjoiMjNlY2I4ZjMtNDRlNS00ZTMyLWEwMjYtYzczNGYzZGY3NTMxIiwidHlwZSI6InJlZnJlc2giLCJzdWIiOnsiaWF0IjoiVHVlLCAzMSBNYXkgMjAyMiAxNDoyNjozNiBHTVQiLCJ0dGwiOjQzMjAwMCwidXNlcl9pZCI6ImNmOThmZTEyLTBkODYtNDY3ZC1iODVkLTI3NmFmNDE1ZjMxMyIsImFjY2Vzc190b2tlbl9pZCI6IjkzNmVmYTVlLTBhZmItNDQ2OC1iYTFmLWIxMTRiNmU1ZWZhYiIsInJlZnJlc2hfdG9rZW5faWQiOiI2OThjMmRmNS0zYTBiLTRhOWItODk0ZC01NzVhNmE2M2FiZWMifSwibmJmIjoxNjU0MDA3MTk2LCJleHAiOjE2NTQ0MzkxOTZ9.-cKVzkM8sbfwfPisvsVVfYi-LGQv7koV6oRIUnXT7JI'
incorrect_jwt_token = 'Bullshit'
correct_uuid = str(uuid.uuid4())
incorrect_uuid = '3aec01aa-3033-4281-964a-5e035e7aac8'

scenarios = [
    Scenario(
        url='/emails/html_templates/',
        method='POST',
        body={"title": "Заголовок", "template": "<p><strong>Hello {{ name }} {{ surname }} </strong>,</p>"},
        headers={'X-Request-Id': correct_uuid, 'Idempotency-Key': correct_uuid, 'Authorization': correct_jwt_token},
        expected_status=201,
        expected_body={"id": correct_uuid, "msg": "Created at 2022-08-28 15:54:26.869732+00:00"},
        check_len_body=True,
        check_len_str_body=True
    ),
]
