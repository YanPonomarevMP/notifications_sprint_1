# Flake8: noqa
# type: ignore
"""Модуль содержит псевдо аут (мок) сервер."""

import uvicorn
from fastapi import FastAPI, Header

app = FastAPI()


@app.post('/v1/back/check_token')
async def check_token(
    authorization: str = Header(),
    x_request_id: str = Header()
) -> dict:

    """Ручка с очень некачественной проверкой токена."""

    print('authorization', authorization)
    print()
    print('x_request_id', x_request_id)

    return {'msg': 'OK'}


@app.get('/v1/back/user_data/email/{email_id}')
async def email(
    email_id: str,
    authorization: str = Header(),
    x_request_id: str = Header()
) -> dict:

    """Ручка возвращает email."""

    print('authorization', authorization),
    print('x_request_id', x_request_id)
    print()
    print('email_id', email_id)

    # TODO: С этим надо что-то сделать, нельзя это оставлять так.
    return {
        'email': 'vladasabelnikova@yandex.ru',
        'name': 'vlada',
        'groups': ['dba8704f-c69a-431c-80e5-d779d537a122', 'dba8704f-c69a-431c-80e5-d779d537a123']
    }


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='localhost',
        port=5000,
    )
