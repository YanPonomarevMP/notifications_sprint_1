# Flake8: noqa
# type: ignore
"""Модуль содержит псевдо аут (мок) сервер."""
from typing import AsyncGenerator, Generator

import uvicorn
from fastapi import FastAPI, Header, WebSocket, Depends

from fastapi.responses import HTMLResponse

from db.message_brokers.rabbit_message_broker import message_broker_factory

app = FastAPI()

# html = """
# <!DOCTYPE html>
# <html>
#     <head>
#         <title>Chat</title>
#     </head>
#     <body>
#         <h1>WebSocket Progress</h1>
#
#         <p id='likes'>0</p>
#         <script>
#             var ws = new WebSocket("ws://localhost:5000/ws_progress");
#             ws.onmessage = function(event) {
#                 var messages = document.getElementById('likes')
#                 messages.innerText = event.data
#             };
#         </script>
#     </body>
# </html>
# """
html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
    <link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons">
    <link rel="stylesheet" href="http://fonts.googleapis.com/css?family=Roboto:300,400,500,700" type="text/css">
    <link rel="stylesheet" href="https://code.getmdl.io/1.3.0/material.purple-indigo.min.css">
    <!--    <link rel="stylesheet" href="mdl.css">-->
    <!--    <link rel="stylesheet" href="styles.css">-->
</head>
<body>
<div class="mdl-layout mdl-js-layout mdl-layout--fixed-header">
    <header class="mdl-layout__header">
        <div class="mdl-layout__header-row">
            <!-- Title -->
            <span class="mdl-layout-title">Title 1</span>
            <!-- Add spacer, to align navigation to the right -->
            <div class="mdl-layout-spacer"></div>
            <!--Search panel-->
            <div class="mdl-textfield mdl-js-textfield mdl-textfield--expandable">
                <label class="mdl-button mdl-js-button mdl-button--icon" for="search">
                    <i class="material-icons">search</i>
                </label>
                <div class="mdl-textfield__expandable-holder">
                    <input class="mdl-textfield__input local-textfield__search mdl-color-text--grey-800" type="text"
                           id="search">

                </div>
            </div>
            <!-- Navigation. We hide it in small screens. -->
            <!--            <nav class="mdl-navigation mdl-layout&#45;&#45;large-screen-only">-->
            <!--                <a class="mdl-navigation__link" href="">Link</a>-->
            <!--                <a class="mdl-navigation__link" href="">Link</a>-->
            <!--                <a class="mdl-navigation__link" href="">Link</a>-->
            <!--                <a class="mdl-navigation__link" href="">Link</a>-->
            <!--            </nav>-->
        </div>
    </header>
    <div class="mdl-layout__drawer">
        <span class="mdl-layout-title">Title</span>
        <nav class="mdl-navigation">
            <a class="mdl-navigation__link" href="">Link</a>
            <a class="mdl-navigation__link" href="">Link</a>
            <a class="mdl-navigation__link" href="">Link</a>
            <a class="mdl-navigation__link" href="">Link</a>
        </nav>
    </div>

    <main class="mdl-layout__content">

        <div class="demo-container mdl-grid">
            <!--            <div class="mdl-cell mdl-cell&#45;&#45;2-col-desktop" style="height: 900px"></div>-->

            <div class="mdl-color--white mdl-color-text--grey-800 mdl-cell mdl-cell--12-col-desktop"
                 style="padding-top: 400px; height: 900px">
                <!-- Simple MDL Progress Bar -->

                <div id="p1" class="mdl-progress mdl-js-progress" style="height: 16px; margin: auto"></div>
                <script>
                    var ws = new WebSocket("ws://localhost:5000/ws_progress");
                    ws.onmessage = function (event) {
                        document.querySelector('#p1').MaterialProgress.setProgress(event.data);
                        document.querySelector('#p1').MaterialProgress.setBuffer(event.data);
                    };

                </script>
            </div>

        </div>
        <footer class="demo-footer mdl-mini-footer">
            <div class="mdl-mini-footer--left-section">
                <ul class="mdl-mini-footer--link-list">
                    <li><a href="#">Help</a></li>
                    <li><a href="#">Privacy and Terms</a></li>
                    <li><a href="#">User Agreement</a></li>
                </ul>
            </div>
        </footer>
    </main>
</div>
<script defer src="https://code.getmdl.io/1.3.0/material.min.js"></script>
</body>
</html>

"""
async def create_liker():
    async def create_like():
        total = 0
        while True:
            total += 1
            yield total
    return create_like()

@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, liker: AsyncGenerator = Depends(create_liker)):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            result = await anext(liker)
            await websocket.send_text(f"{result}")
    except Exception as error:
        print(error)

def callback(websocket: WebSocket):

    async def inner(message):
        await websocket.send_text(f"{message.body.decode()}")
        await message.ack()

    return inner


@app.websocket("/ws_progress")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await message_broker_factory.consume('websocket_progress', callback=callback(websocket))

    # try:
    #     while True:
    #
    #
    #
    #         await websocket.send_text(f"{result}")
    # except Exception as error:
    #     print(error)


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
