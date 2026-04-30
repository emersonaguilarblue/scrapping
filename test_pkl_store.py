"""Pruebas para src.storage.pkl_store."""
from pathlib import Path

import pytest
from pydantic import HttpUrl

from src.core.exceptions import StorageError
from src.core.models import ScrapedDocument
from src.storage.pkl_store import PklStore


def _make_doc(sid: str, category: str = "otros") -> ScrapedDocument:
    return ScrapedDocument(
        source_id=sid,
        url=HttpUrl(f"https://example.com/{sid}"),
        title=f"Title {sid}",
        content=f"Content {sid}",
        chunks=[f"Chunk1 {sid}", f"Chunk2 {sid}"],
        metadata={
            "category": category,
            "strategy": "static",
            "breadcrumb": "x > y",
            "content_length": 9,
        },
        content_hash=f"hash_{sid}",
    )


class TestPklStore:
    def test_raises_when_no_documents(self, tmp_path: Path) -> None:
        store = PklStore(tmp_path)
        with pytest.raises(StorageError):
            store.export([])

    def test_exports_pkl_and_xlsx(self, tmp_path: Path) -> None:
        store = PklStore(tmp_path)
        docs = [_make_doc("a", "legal"), _make_doc("b", "otros")]
        saved = store.export(docs)

        assert "documents" in saved
        assert "chunks" in saved
        assert "xlsx" in saved
        assert (tmp_path / "documents.pkl").exists()
        assert (tmp_path / "chunks.pkl").exists()
        assert (tmp_path / "documents.xlsx").exists()

    def test_partitions_by_category(self, tmp_path: Path) -> None:
        store = PklStore(tmp_path)
        docs = [_make_doc("a", "legal"), _make_doc("b", "otros")]
        saved = store.export(docs)
        assert "docs_legal" in saved
        assert "docs_otros" in saved
