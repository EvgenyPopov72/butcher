import tornado.web

from db import DBInterface


class ChunksHandler(tornado.web.RequestHandler):
    """Chunks Handler."""

    async def get(self):
        dbi: DBInterface = self.settings["dbi"]
        chunks = await dbi.list_chunks()
        await self.render("chunks.html", chunks=chunks)
