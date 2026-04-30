"""Pruebas para src.storage (cache, jsonl_store, raw_store)."""
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from pydantic import HttpUrl

from src.core.models import RawPayload, ScrapedDocument
from src.storage.cache import RawPayloadCache
from src.storage.jsonl_store import JsonlDocumentStore
from src.storage.raw_store import RawFileStore


@pytest.fixture
def raw_payload() -> RawPayload:
    return RawPayload(
        source_id="src1",
        url=HttpUrl("https://example.com/x"),
        content_type="text/html; charset=utf-8",
        body=b"<html>hi</html>",
        fetched_at=datetime.utcnow(),
        status_code=200,
    )


@pytest.fixture
def doc() -> ScrapedDocument:
    return ScrapedDocument(
        source_id="src1",
        url=HttpUrl("https://example.com/x"),
        title="t",
        content="c",
        chunks=["c"],
        content_hash="h",
    )


class TestRawPayloadCache:
    def test_get_returns_none_when_missing(self, tmp_path: Path) -> None:
        cache = RawPayloadCache(tmp_path, ttl_hours=1)
        assert cache.get("nope") is None

    def test_set_then_get_roundtrip(self, tmp_path: Path, raw_payload: RawPayload) -> None:
        cache = RawPayloadCache(tmp_path, ttl_hours=1)
        cache.set("k1", raw_payload)
        loaded = cache.get("k1")
        assert loaded is not None
        assert loaded.source_id == raw_payload.source_id
        assert loaded.body == raw_payload.body

    def test_returns_none_when_stale(self, tmp_path: Path, raw_payload: RawPayload) -> None:
        cache = RawPayloadCache(tmp_path, ttl_hours=1)
        old = raw_payload.model_copy(
            update={"fetched_at": datetime.utcnow() - timedelta(hours=10)}
        )
        cache.set("k1", old)
        assert cache.get("k1") is None


class TestJsonlDocumentStore:
    def test_save_appends_line(self, tmp_path: Path, doc: ScrapedDocument) -> None:
        store = JsonlDocumentStore(tmp_path)
        store.save(doc)
        store.save(doc)
        loaded = store.load_all()
        assert len(loaded) == 2
        assert loaded[0].source_id == "src1"

    def test_load_all_empty_when_missing(self, tmp_path: Path) -> None:
        store = JsonlDocumentStore(tmp_path)
        assert store.load_all() == []

    def test_reset_removes_file(self, tmp_path: Path, doc: ScrapedDocument) -> None:
        store = JsonlDocumentStore(tmp_path)
        store.save(doc)
        assert store.path.exists()
        store.reset()
        assert not store.path.exists()

    def test_reset_idempotent(self, tmp_path: Path) -> None:
        store = JsonlDocumentStore(tmp_path)
        store.reset()  # No debe fallar


class TestRawFileStore:
    def test_extension_for_pdf(self) -> None:
        assert RawFileStore._extension_for("application/pdf") == ".pdf"

    def test_extension_for_html(self) -> None:
        assert RawFileStore._extension_for("text/html; charset=utf-8") == ".html"

    def test_extension_for_unknown(self) -> None:
        assert RawFileStore._extension_for("image/png") == ".bin"

    def test_save_writes_bytes(self, tmp_path: Path, raw_payload: RawPayload) -> None:
        store = RawFileStore(tmp_path)
        path = store.save(raw_payload)
        assert path.exists()
        assert path.read_bytes() == raw_payload.body
        assert path.suffix == ".html"
