from db.storage.abstract_classes import AbstractDBClient


class HtmlTemplatesFactory:
    def __init__(self, orm: AbstractDBClient):
        self.orm = orm

    async def execute(self):
        pass