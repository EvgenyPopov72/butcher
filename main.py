import asyncio
import logging
import os
from pathlib import Path

from tornado.web import Application, url
from tornado.options import define, options, parse_command_line

from db import DBInterface
from handlers import ChunksHandler, JobsHandler, UploadFileHandler

log = logging.getLogger("Gabumas.main")

define("port", default=8888, help="run on the given port", type=int)


def make_app():
    """Create Application object."""
    # TODO add settings config in external file (e.g. some *.yaml, *.toml)

    db_creds = {
        "host": os.getenv("POSTGRES_HOST", "127.0.0.1"),
        "port": os.getenv("POSTGRES_PORT", 5432),
        "username": os.getenv("POSTGRES_USER", "gabumas"),
        "password": os.getenv("POSTGRES_PASSWORD", "pass1234"),
        "database": os.getenv("POSTGRES_DB", "gabumas"),
    }
    dbi = DBInterface(**db_creds)

    base_path = Path(__file__).parent.resolve()
    settings = {
        "debug": True,
        "cookie_secret": "some secret",
        "template_path": base_path / "templates",
        "upload_path": base_path / "uploads",
        "chunks": base_path / "chunks",
        "static_path": base_path / "chunks",
        "dbi": dbi,
    }

    return Application(
        [
            url(r"/", UploadFileHandler, name="files"),
            url(r"/jobs", JobsHandler, name="jobs"),
            url(r"/chunks", ChunksHandler, name="chunks"),
        ],
        **settings,
    )


async def main():
    parse_command_line()
    log.info("Start server on port: %d", options.port)
    app = make_app()
    await app.settings["dbi"].connect()
    app.listen(options.port)

    shutdown_event = asyncio.Event()
    await shutdown_event.wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Server is stopping.")
