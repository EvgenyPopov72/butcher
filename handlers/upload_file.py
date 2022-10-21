from pathlib import Path

import tornado.web
from tornado.ioloop import IOLoop

from db import DBInterface
from tasks import CutVideo


class UploadFileHandler(tornado.web.RequestHandler):
    """Files Handler."""

    async def get(self):
        uploaded_file = self.get_secure_cookie("uploaded_file")
        self.clear_cookie("uploaded_file")

        dbi: DBInterface = self.settings["dbi"]
        files = await dbi.list_files()
        await self.render("files.html", uploaded_file=uploaded_file, files=files)

    async def post(self):
        uploaded_file = (
                self.request.files and
                self.request.files.get("upload-video-file") and
                self.request.files.get("upload-video-file")[0]
        )

        if uploaded_file:
            file_path = Path(self.settings["upload_path"], uploaded_file["filename"])
            with open(file_path, "wb") as output_file:
                output_file.write(uploaded_file["body"])

            self.set_secure_cookie("uploaded_file", uploaded_file["filename"])

            dbi: DBInterface = self.settings["dbi"]
            await dbi.save_file(uploaded_file["filename"], pitch=int(self.get_argument("pitch-speed")))

            task = CutVideo(self.settings["upload_path"], self.settings["chunks"], dbi)
            IOLoop.current().spawn_callback(task.start, uploaded_file["filename"])

        self.redirect("/")
