# Flake8: noqa
# type: ignore
"""Модуль содержит псевдо аут (мок) сервер."""
import uvicorn
from fastapi import FastAPI, Header

app = FastAPI()


@app.post('/v1/back/check_token')
async def check_token(
    authorization: str = Header(None),
    x_request_id: str = Header(None)
) -> dict:

    """Ручка с очень некачественной проверкой токена."""

    print('authorization', authorization)
    print()
    print('x_request_id', x_request_id)

    return {'msg': 'OK'}


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='localhost',
        port=5000,
    )
