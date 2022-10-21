from handlers import BaseHandler
from utils import JobStatus


class JobsHandler(BaseHandler):
    """Job Handler."""

    async def get(self):
        jobs = await self.dbi.list_jobs()
        await self.render(
            "jobs.html",
            jobs=map(
                lambda job: dict(job, status=JobStatus(job["status"]).name),  # get job's status name by int value
                jobs
            )
        )
