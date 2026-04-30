"""Fixtures compartidas para la suite de pruebas."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest
from pydantic import HttpUrl

from src.config.settings import Settings
from src.core.enums import ScrapeStrategy, SourceCategory
from src.core.models import PageSource, RawPayload, ScrapedDocument


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    """Settings aislados con directorios temporales."""
    s = Settings(
        raw_dir=tmp_path / "raw",
        processed_dir=tmp_path / "processed",
        cache_dir=tmp_path / "cache",
        max_concurrency=2,
        retry_attempts=1,
        cache_ttl_hours=1,
        chunk_size=500,
        chunk_overlap=50,
    )
    s.ensure_dirs()
    return s


@pytest.fixture
def page_source() -> PageSource:
    return PageSource(
        id="test_source",
        name="Test Source",
        url=HttpUrl("https://example.com/test"),
        category=SourceCategory.OTROS,
        strategy=ScrapeStrategy.STATIC,
        breadcrumb="Hogar > Test",
    )


@pytest.fixture
def raw_html_payload() -> RawPayload:
    return RawPayload(
        source_id="test_source",
        url=HttpUrl("https://example.com/test"),
        content_type="text/html; charset=utf-8",
        body=b"<html><body><h1>Hola</h1><p>Mundo</p></body></html>",
        fetched_at=datetime(2026, 1, 1, 12, 0, 0),
        status_code=200,
    )


@pytest.fixture
def scraped_document() -> ScrapedDocument:
    return ScrapedDocument(
        source_id="test_source",
        url=HttpUrl("https://example.com/test"),
        title="Hola",
        content="Mundo",
        chunks=["Mundo"],
        metadata={"category": "otros"},
        content_hash="abc123",
    )
