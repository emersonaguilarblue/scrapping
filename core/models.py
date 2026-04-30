from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from src.core.enums import ScrapeStrategy, SourceCategory


class PageSource(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    name: str
    url: HttpUrl
    category: SourceCategory
    strategy: ScrapeStrategy
    breadcrumb: str | None = None
    wait_selector: str | None = None
    extra: dict[str, Any] = Field(default_factory=dict)


class RawPayload(BaseModel):
    source_id: str
    url: HttpUrl
    content_type: str
    body: bytes
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    status_code: int | None = None
    final_url: HttpUrl | None = None


class ScrapedDocument(BaseModel):
    source_id: str
    url: HttpUrl
    title: str
    content: str
    markdown: str = ""
    chunks: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    content_hash: str
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
