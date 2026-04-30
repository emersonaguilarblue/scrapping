import json
from datetime import datetime, timedelta
from pathlib import Path

from loguru import logger
from pydantic import HttpUrl

from src.core.interfaces import ICache
from src.core.models import RawPayload


class RawPayloadCache(ICache):
    def __init__(self, cache_dir: Path, ttl_hours: int) -> None:
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)

    def _meta_path(self, key: str) -> Path:
        return self.cache_dir / f"{key}.json"

    def _body_path(self, key: str) -> Path:
        return self.cache_dir / f"{key}.bin"

    def get(self, key: str) -> RawPayload | None:
        meta = self._meta_path(key)
        body = self._body_path(key)
        if not meta.exists() or not body.exists():
            return None

        data = json.loads(meta.read_text(encoding="utf-8"))
        fetched_at = datetime.fromisoformat(data["fetched_at"])
        if datetime.utcnow() - fetched_at > self.ttl:
            logger.debug(f"cache stale: {key}")
            return None

        return RawPayload(
            source_id=data["source_id"],
            url=HttpUrl(data["url"]),
            content_type=data["content_type"],
            body=body.read_bytes(),
            fetched_at=fetched_at,
            status_code=data.get("status_code"),
            final_url=HttpUrl(data["final_url"]) if data.get("final_url") else None,
        )

    def set(self, key: str, payload: RawPayload) -> None:
        self._body_path(key).write_bytes(payload.body)
        meta = {
            "source_id": payload.source_id,
            "url": str(payload.url),
            "content_type": payload.content_type,
            "fetched_at": payload.fetched_at.isoformat(),
            "status_code": payload.status_code,
            "final_url": str(payload.final_url) if payload.final_url else None,
        }
        self._meta_path(key).write_text(
            json.dumps(meta, ensure_ascii=False), encoding="utf-8"
        )
