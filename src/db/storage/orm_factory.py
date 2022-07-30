import databases

from config.settings import config


class AsyncPGClient:

    def __init__(self):
        user = config.pg.login.get_secret_value()
        password = config.pg.password.get_secret_value()
        host = config.pg.host
        db_name = config.pg.db_name
        self.session = databases.Database(f'postgresql://{user}:{password}@{host}/{db_name}')

    async def start(self):
        await self.session.connect()

    async def stop(self):
        await self.session.disconnect()


# class Storage:
#
#     def __init__(self, client):
