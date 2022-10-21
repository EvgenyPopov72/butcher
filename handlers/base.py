import tornado.web

from db import DBInterface


class BaseHandler(tornado.web.RequestHandler):
    """Base handler."""

    def initialize(self) -> None:
        self.dbi: DBInterface = self.settings["dbi"]
