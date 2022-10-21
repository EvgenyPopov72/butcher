from db import DBInterface
from handlers import BaseHandler


class ChunksHandler(BaseHandler):
    """Chunks Handler."""

    async def get(self):
        dbi: DBInterface = self.settings["dbi"]
        chunks = await dbi.list_chunks()
        await self.render("chunks.html", chunks=chunks)
