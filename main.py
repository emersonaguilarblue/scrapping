import argparse
import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from loguru import logger

from src.config.settings import get_settings
from src.config.sources import get_source, list_sources
from src.parsers.factory import ParserFactory
from src.pipeline.chunker import Chunker
from src.pipeline.orchestrator import Orchestrator
from src.scrapers.factory import ScraperFactory
from src.storage.cache import RawPayloadCache
from src.storage.jsonl_store import JsonlDocumentStore
from src.storage.pkl_store import PklStore
from src.storage.raw_store import RawFileStore


def _configure_logging(level: str) -> None:
    logger.remove()
    logger.add(sys.stderr, level=level)


def _build_orchestrator() -> Orchestrator:
    settings = get_settings()
    _configure_logging(settings.log_level)
    return Orchestrator(
        settings=settings,
        scraper_factory=ScraperFactory(settings),
        parser_factory=ParserFactory(),
        document_store=JsonlDocumentStore(settings.processed_dir),
        raw_store=RawFileStore(settings.raw_dir),
        cache=RawPayloadCache(settings.cache_dir, settings.cache_ttl_hours),
        chunker=Chunker(settings.chunk_size, settings.chunk_overlap),
    )


async def run_async(source_ids: list[str] | None, reset: bool) -> int:
    orchestrator = _build_orchestrator()
    if reset:
        orchestrator.documents.reset()

    sources = (
        [get_source(sid) for sid in source_ids]
        if source_ids
        else list(list_sources())
    )
    docs = await orchestrator.run(sources)

    if docs:
        settings = get_settings()
        pkl = PklStore(settings.processed_dir)
        pkl.export(docs if reset else orchestrator.documents.load_all())

    return 0 if docs else 1


def cli() -> None:
    parser = argparse.ArgumentParser(prog="claro-scrap")
    sub = parser.add_subparsers(dest="cmd", required=True)

    run = sub.add_parser("run", help="Scrape sources")
    run.add_argument("--ids", nargs="*", help="Source ids (default: all)")
    run.add_argument("--reset", action="store_true", help="Truncate jsonl before run")

    sub.add_parser("list", help="List configured sources")

    sub.add_parser("export", help="Export JSONL to pickle (docs + chunks + partitions by category)")

    args = parser.parse_args()

    if args.cmd == "list":
        for s in list_sources():
            print(f"{s.id:30s} {s.strategy.value:8s} {s.url}")
        return

    if args.cmd == "run":
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            rc = loop.run_until_complete(run_async(args.ids, args.reset))
        finally:
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.run_until_complete(loop.shutdown_default_executor())
            loop.close()
        sys.exit(rc)

    if args.cmd == "export":
        settings = get_settings()
        _configure_logging(settings.log_level)
        store = JsonlDocumentStore(settings.processed_dir)
        docs = store.load_all()
        if not docs:
            logger.error("No documents found. Run scraping first.")
            sys.exit(1)
        pkl = PklStore(settings.processed_dir)
        saved = pkl.export(docs)
        for key, path in saved.items():
            print(f"{key:30s} -> {path}")
        sys.exit(0)


if __name__ == "__main__":
    cli()
