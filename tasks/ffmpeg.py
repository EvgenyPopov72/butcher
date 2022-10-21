from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from db import DBInterface
from utils import JobStatus

log = logging.getLogger("Gabumas.ffmpeg")


class CutVideo:
    def __init__(self, input_dir: str | Path, output_dir: str | Path, dbi: DBInterface):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.dbi = dbi

    async def start(self, file_name: str, chunk_duration: int = 1):
        job_id = await self.dbi.create_job(file_name)

        job_output_dir = self.output_dir / str(job_id)
        job_output_dir.mkdir(parents=True, exist_ok=True)
        playlist_file_name = job_output_dir / f"{Path(file_name).stem}.m3u8"
        full_path_input_file = self.input_dir / file_name

        cmd = f"""ffmpeg -i {full_path_input_file} \
             -c:v h264 \
             -flags +cgop \
             -g 30 \
             -hls_time {chunk_duration} \
             '{playlist_file_name}'
         """
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)

        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            log.error(stderr)
            await self.dbi.update_job(job_id, JobStatus.FAILED.value)
            return

        chunk_files = [
            str(file_name.relative_to(self.output_dir))
            for file_name in job_output_dir.iterdir()
            if file_name.is_file()
        ]

        await self.dbi.save_chunks(file_name, chunk_files)
        await self.dbi.update_job(job_id, JobStatus.SUCCESSFUL.value)

