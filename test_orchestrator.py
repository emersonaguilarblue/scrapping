"""Pruebas para src.pipeline.orchestrator con dependencias mockeadas."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import HttpUrl

from src.core.enums import ScrapeStrategy, SourceCategory
from src.core.models import PageSource, RawPayload, ScrapedDocument
from src.pipeline.chunker import Chunker
from src.pipeline.orchestrator import Orchestrator


def _source(sid: str = "s1") -> PageSource:
    return PageSource(
        id=sid,
        name=sid,
        url=HttpUrl(f"https://example.com/{sid}"),
        category=SourceCategory.OTROS,
        strategy=ScrapeStrategy.STATIC,
    )


def _payload(sid: str = "s1") -> RawPayload:
    return RawPayload(
        source_id=sid,
        url=HttpUrl(f"https://example.com/{sid}"),
        content_type="text/html",
        body=b"hi",
    )


def _document(sid: str = "s1") -> ScrapedDocument:
    return ScrapedDocument(
        source_id=sid,
        url=HttpUrl(f"https://example.com/{sid}"),
        title="t",
        content="contenido extenso de prueba",
        content_hash="h",
    )


def _build(settings, scraper_returns=None, parser_returns=None, cache_hit=None):
    scraper = MagicMock()
    scraper.fetch = AsyncMock(return_value=scraper_returns or _payload())
    scraper_factory = MagicMock()
    scraper_factory.get.return_value = scraper

    parser = MagicMock()
    parser.parse.return_value = parser_returns or _document()
    parser_factory = MagicMock()
    parser_factory.get.return_value = parser

    documents = MagicMock()
    raw = MagicMock()
    cache = MagicMock()
    cache.get.return_value = cache_hit
    cache.set = MagicMock()

    return Orchestrator(
        settings=settings,
        scraper_factory=scraper_factory,
        parser_factory=parser_factory,
        document_store=documents,
        raw_store=raw,
        cache=cache,
        chunker=Chunker(chunk_size=10, overlap=2),
    ), scraper, parser, cache, raw, documents


class TestOrchestrator:
    @pytest.mark.asyncio
    async def test_run_with_cache_miss_calls_scraper(self, settings) -> None:
        orch, scraper, parser, cache, raw, documents = _build(settings)
        result = await orch.run([_source("s1")])
        assert len(result) == 1
        scraper.fetch.assert_awaited_once()
        raw.save.assert_called_once()
        cache.set.assert_called_once()
        documents.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_with_cache_hit_skips_scraper(self, settings) -> None:
        orch, scraper, parser, cache, raw, documents = _build(
            settings, cache_hit=_payload("s1")
        )
        await orch.run([_source("s1")])
        scraper.fetch.assert_not_called()
        raw.save.assert_not_called()

    @pytest.mark.asyncio
    async def test_run_continues_after_failure(self, settings) -> None:
        orch, scraper, parser, cache, raw, documents = _build(settings)
        # El scraper falla en el primer source pero el segundo procede
        scraper.fetch = AsyncMock(side_effect=[RuntimeError("boom"), _payload("s2")])
        result = await orch.run([_source("s1"), _source("s2")])
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_chunks_are_assigned(self, settings) -> None:
        orch, *_ = _build(settings)
        result = await orch.run([_source("s1")])
        assert len(result[0].chunks) >= 1
