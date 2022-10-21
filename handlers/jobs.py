from db import DBInterface
from handlers import BaseHandler
from utils import JobStatus


class JobsHandler(BaseHandler):
    """Job Handler."""

    async def get(self):
        dbi: DBInterface = self.settings["dbi"]
        jobs = await dbi.list_jobs()
        await self.render(
            "jobs.html",
            jobs=map(
                lambda job: dict(job, status=JobStatus(job["status"]).name),  # get job's status name by int value
                jobs
            )
        )
