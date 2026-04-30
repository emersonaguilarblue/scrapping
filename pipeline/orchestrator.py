import asyncio

from loguru import logger

from src.config.settings import Settings
from src.core.exceptions import ScrapingPipelineError
from src.core.models import PageSource, ScrapedDocument
from src.parsers.factory import ParserFactory
from src.pipeline.chunker import Chunker
from src.scrapers.factory import ScraperFactory
from src.storage.cache import RawPayloadCache
from src.storage.jsonl_store import JsonlDocumentStore
from src.storage.raw_store import RawFileStore


class Orchestrator:
    def __init__(
        self,
        settings: Settings,
        scraper_factory: ScraperFactory,
        parser_factory: ParserFactory,
        document_store: JsonlDocumentStore,
        raw_store: RawFileStore,
        cache: RawPayloadCache,
        chunker: Chunker,
    ) -> None:
        self.settings = settings
        self.scrapers = scraper_factory
        self.parsers = parser_factory
        self.documents = document_store
        self.raw = raw_store
        self.cache = cache
        self.chunker = chunker
        self._semaphore = asyncio.Semaphore(settings.max_concurrency)

    async def run(self, sources: list[PageSource]) -> list[ScrapedDocument]:
        tasks = [self._process_one(s) for s in sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        documents: list[ScrapedDocument] = []
        for source, result in zip(sources, results, strict=True):
            if isinstance(result, Exception):
                logger.error(f"FAIL {source.id}: {result}")
                continue
            documents.append(result)
            self.documents.save(result)

        logger.info(f"Done: {len(documents)}/{len(sources)} ok")
        return documents

    async def _process_one(self, source: PageSource) -> ScrapedDocument:
        async with self._semaphore:
            try:
                payload = self.cache.get(source.id)
                if payload is None:
                    scraper = self.scrapers.get(source.strategy)
                    payload = await scraper.fetch(source)
                    self.raw.save(payload)
                    self.cache.set(source.id, payload)
                else:
                    logger.info(f"[cache hit] {source.id}")

                parser = self.parsers.get(source.strategy)
                document = parser.parse(source, payload)
                chunk_source = document.markdown or document.content
                document.chunks = self.chunker.split(chunk_source)
                logger.success(
                    f"OK {source.id} chars={len(document.content)} "
                    f"md={len(document.markdown)} chunks={len(document.chunks)}"
                )
                return document
            except Exception as exc:
                raise ScrapingPipelineError(f"{source.id}: {exc}") from exc
