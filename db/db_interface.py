import logging
from typing import Iterable

import asyncpg

from utils import JobStatus

log = logging.getLogger("Gabumas.dbi")


class DBInterface:
    """DB interface."""

    def __init__(self, host: str, port: int, *, username: str, password: str, database: str):
        self.pool = None
        self.host = host
        self.port = port
        self.dsn = f"postgres://{username}:{password}@{host}:{port}/{database}"

    async def connect(self):
        """Create connection pool to Postgres DB."""

        log.info("Connecting to database at %s:%s", self.host, self.port)
        self.pool = await asyncpg.create_pool(dsn=self.dsn)
        log.info("Connected to database")

    async def save_file(self, filename: str, pitch: int):
        """Save info of new file to db."""
        async with self.pool.acquire() as connection:
            await connection.execute("INSERT INTO files(name, pitch) VALUES($1, $2)", filename, pitch)

    async def list_files(self):
        """List all files in db."""
        async with self.pool.acquire() as connection:
            return await connection.fetch("SELECT id, name, pitch, created_at FROM files ORDER BY created_at DESC")

    async def list_jobs(self):
        """List all jobs in db."""
        async with self.pool.acquire() as connection:
            return await connection.fetch("""
                SELECT j.id, f.name as original_file, j.created_at, j.updated_at, j.status FROM jobs j
                JOIN files f on f.id = j.file
                ORDER BY j.updated_at DESC
            """)

    async def create_job(self, filename: str):
        """Save info of new job to db."""
        async with self.pool.acquire() as connection:
            return await connection.fetchval("""
                INSERT INTO jobs(file, status)
                SELECT id, $2 FROM files WHERE name = $1
                RETURNING id
                """, filename, JobStatus.STARTED.value
            )

    async def update_job(self, job_id: int, status: int):
        """Update job status."""
        async with self.pool.acquire() as connection:
            return await connection.execute("UPDATE jobs SET status = $2 WHERE id = $1", job_id, status)

    async def list_chunks(self):
        """List all chinks in db."""
        async with self.pool.acquire() as connection:
            return await connection.fetch("""
                SELECT c.id, c.name as chunk_file, f.name as original_file, c.created_at FROM chunks c
                JOIN files f on f.id = c.file
                ORDER BY f.name, c.name
            """)

    async def save_chunks(self, original_file_name: str, chunk_files: Iterable):
        """Save info about chinks to db."""
        async with self.pool.acquire() as connection:
            original_file_pk = await connection.fetchval(
                "SELECT id as original_file FROM files WHERE name = $1",
                original_file_name
            )
            # TODO add populate the database in batches
            rows = [(file_name, original_file_pk) for file_name in chunk_files]
            await connection.executemany("INSERT INTO chunks(name, file) VALUES ($1, $2)", rows)
