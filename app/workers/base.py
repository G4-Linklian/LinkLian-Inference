import asyncio
import os
from abc import ABC, abstractmethod

import redis.asyncio as aioredis
from bullmq import Worker

from app.core.logger import AppLogger

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD") or None

REDIS_CONN_OPTS: dict = {"host": REDIS_HOST, "port": REDIS_PORT}
if REDIS_PASSWORD:
    REDIS_CONN_OPTS["password"] = REDIS_PASSWORD


class BaseWorker(ABC):
    queue_name: str = ""

    def __init__(self) -> None:
        if not self.queue_name:
            raise ValueError(
                f"{self.__class__.__name__} must define queue_name")
        self.logger = AppLogger()
        self._worker: Worker | None = None

    # ── hooks ──────────────────────────────────────────────────────────────────

    async def on_startup(self) -> None:
        """Override to load model or prepare resources before accepting jobs"""

    async def on_shutdown(self) -> None:
        """Override to clean up resources after stopping"""

    # ── abstract ───────────────────────────────────────────────────────────────

    @abstractmethod
    async def process(self, job, job_token):
        """Business logic for each worker — must be implemented in subclass"""

    # ── Redis helper ──────────────────────────────────────────────────────────

    def new_redis(self, *, decode_responses: bool = False) -> aioredis.Redis:
        """
        Create a new async Redis client with a single connection.
        Should be used with async with or try/finally + aclose()
        """
        return aioredis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            decode_responses=decode_responses,
        )

    # ── lifecycle ─────────────────────────────────────────────────────────────

    def _create_bullmq_worker(self) -> Worker:
        """Create a BullMQ Worker bound to the subclass process() method"""
        return Worker(
            self.queue_name,
            self.process,
            {
                "connection": REDIS_CONN_OPTS,
                "lockDuration": 300000,   # 300s
                "lockRenewTime": 60000,   # 60s
            },
        )

    async def run(self) -> None:
        """
        Start the worker.
        Order: on_startup → process jobs → on_shutdown
        """
        class_name = self.__class__.__name__

        self.logger.log(f"[{class_name}] Starting up...", class_name)
        await self.on_startup()

        self._worker = self._create_bullmq_worker()
        self.logger.log(
            f"[{class_name}] Listening on queue '{self.queue_name}'", class_name
        )

        try:
            while True:
                await asyncio.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            pass
        finally:
            self.logger.log(f"[{class_name}] Shutting down...", class_name)
            await self.on_shutdown()
            if self._worker:
                await self._worker.close()
            self.logger.log(f"[{class_name}] Stopped.", class_name)
