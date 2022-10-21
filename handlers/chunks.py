from handlers import BaseHandler


class ChunksHandler(BaseHandler):
    """Chunks Handler."""

    async def get(self):
        chunks = await self.dbi.list_chunks()
        await self.render("chunks.html", chunks=chunks)
