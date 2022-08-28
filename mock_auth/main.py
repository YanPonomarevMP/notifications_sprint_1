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

    return {
        'email': ...,
        'name': 'vlada',
        'groups': ['52186b1b-7e44-419c-b040-c41e815a6308', 'dba8704f-c69a-431c-80e5-d779d537a123']
    }


@app.get('/v1/back/by_group/{group_id}')
async def email(
    group_id: str,
    authorization: str = Header(),
    x_request_id: str = Header()
) -> list:

    """Ручка возвращает всех пользователей с группой group_id."""

    print('authorization', authorization),
    print('x_request_id', x_request_id)
    print()
    print('email_id', group_id)

    return [
        {'user_id': 'c9df603e-62d1-467c-b795-e3ecb78e357a', 'hours': 3, 'minutes': 0},
        {'user_id': '3568b0fd-4a29-4bf6-ab20-916145bf499f', 'hours': -2, 'minutes': 30}
    ]


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='localhost',
        port=5000,
    )
