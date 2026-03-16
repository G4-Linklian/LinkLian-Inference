import json
import os
import time
from typing import Awaitable, Callable, TypedDict

import redis.asyncio as aioredis

from app.core.logger import AppLogger


class ChatMessage(TypedDict):
    role: str
    content: str
    time: int


class AiRedisService:
    def __init__(self) -> None:
        self.message_ttl_seconds = int(os.getenv("AI_CHAT_REDIS_TTL_SECONDS", "60"))
        self.max_history = int(os.getenv("AI_CHAT_MAX_HISTORY", "20"))
        self.logger = AppLogger()
        self._redis = aioredis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            password=os.getenv("REDIS_PASSWORD") or None,
            decode_responses=True,
        )

    async def close(self) -> None:
        await self._redis.aclose()

    async def get_chat_history(
        self,
        chat_id: str | int,
        get_messages_from_db: Callable[[], Awaitable[list[ChatMessage]]] | None = None,
    ) -> list[ChatMessage]:
        key = f"chat:{chat_id}:messages"
        history = await self._redis.lrange(key, 0, -1)

        if len(history) == 0 and get_messages_from_db is not None:
            db_messages = await get_messages_from_db()

            if len(db_messages) > 0:
                payloads = [json.dumps(message) for message in db_messages]
                await self._redis.rpush(key, *payloads)
                await self._redis.expire(key, self.message_ttl_seconds)

            return db_messages

        parsed: list[ChatMessage] = []
        for item in history:
            try:
                message = json.loads(item)
                if isinstance(message, dict):
                    parsed.append(
                        {
                            "role": str(message.get("role", "")),
                            "content": str(message.get("content", "")),
                            "time": int(message.get("time", 0) or 0),
                        }
                    )
            except Exception:
                self.logger.warn(
                    "Invalid chat message in redis history",
                    "AiRedisService",
                )

        return parsed

    async def add_message(
        self,
        chat_id: str | int,
        role: str,
        content: str,
    ) -> None:
        messages_key = f"chat:{chat_id}:messages"
        activity_key = f"chat:{chat_id}:last_activity"

        message: ChatMessage = {
            "role": role,
            "content": content,
            "time": int(time.time() * 1000),
        }

        await self._redis.rpush(messages_key, json.dumps(message, ensure_ascii=False))
        await self._redis.ltrim(messages_key, -self.max_history, -1)
        await self._redis.expire(messages_key, self.message_ttl_seconds)

        await self._redis.set(activity_key, int(time.time() * 1000))
        await self._redis.expire(activity_key, self.message_ttl_seconds)

    async def set_docs_overview(
        self,
        chat_id: str | int,
        docs_overview: str,
    ) -> None:
        docs_overview_key = f"chat:{chat_id}:docs_overview"
        activity_key = f"chat:{chat_id}:last_activity"

        await self._redis.set(docs_overview_key, docs_overview)
        await self._redis.expire(docs_overview_key, self.message_ttl_seconds)

        await self._redis.set(activity_key, int(time.time() * 1000))
        await self._redis.expire(activity_key, self.message_ttl_seconds)

    async def get_docs_overview(self, chat_id: str | int) -> str | None:
        docs_overview_key = f"chat:{chat_id}:docs_overview"
        return await self._redis.get(docs_overview_key)

    async def clear_chat_session(self, chat_id: str | int) -> int:
        messages_key = f"chat:{chat_id}:messages"
        chat_history_key = f"chat:{chat_id}:chat_history"
        docs_overview_key = f"chat:{chat_id}:docs_overview"
        activity_key = f"chat:{chat_id}:last_activity"

        return await self._redis.delete(
            messages_key,
            chat_history_key,
            docs_overview_key,
            activity_key,
        )

    async def get_last_activity(self, chat_id: str | int) -> int | None:
        activity_key = f"chat:{chat_id}:last_activity"
        value = await self._redis.get(activity_key)

        if value is None:
            return None

        try:
            return int(value)
        except Exception:
            return None
