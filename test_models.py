"""Pruebas para src.core.models y src.core.enums."""
import pytest
from pydantic import HttpUrl, ValidationError

from src.core.enums import ScrapeStrategy, SourceCategory
from src.core.models import PageSource, RawPayload, ScrapedDocument


class TestEnums:
    def test_scrape_strategy_values(self) -> None:
        assert ScrapeStrategy.STATIC.value == "static"
        assert ScrapeStrategy.DYNAMIC.value == "dynamic"
        assert ScrapeStrategy.PDF.value == "pdf"
        assert ScrapeStrategy.LITHO_API.value == "litho_api"

    def test_source_category_has_legal(self) -> None:
        assert SourceCategory.LEGAL.value == "legal"


class TestPageSource:
    def test_minimum_fields(self) -> None:
        p = PageSource(
            id="x",
            name="X",
            url=HttpUrl("https://a.com"),
            category=SourceCategory.OTROS,
            strategy=ScrapeStrategy.STATIC,
        )
        assert p.id == "x"
        assert p.breadcrumb is None
        assert p.extra == {}

    def test_is_frozen(self) -> None:
        p = PageSource(
            id="x",
            name="X",
            url=HttpUrl("https://a.com"),
            category=SourceCategory.OTROS,
            strategy=ScrapeStrategy.STATIC,
        )
        with pytest.raises(ValidationError):
            p.id = "y"  # type: ignore[misc]

    def test_invalid_url_rejected(self) -> None:
        with pytest.raises(ValidationError):
            PageSource(
                id="x",
                name="X",
                url="no-es-url",  # type: ignore[arg-type]
                category=SourceCategory.OTROS,
                strategy=ScrapeStrategy.STATIC,
            )


class TestRawPayload:
    def test_default_fetched_at_is_set(self) -> None:
        p = RawPayload(
            source_id="x",
            url=HttpUrl("https://a.com"),
            content_type="text/html",
            body=b"hi",
        )
        assert p.fetched_at is not None
        assert p.status_code is None


class TestScrapedDocument:
    def test_defaults(self) -> None:
        d = ScrapedDocument(
            source_id="x",
            url=HttpUrl("https://a.com"),
            title="t",
            content="c",
            content_hash="h",
        )
        assert d.chunks == []
        assert d.metadata == {}

    def test_serialize_roundtrip(self) -> None:
        d = ScrapedDocument(
            source_id="x",
            url=HttpUrl("https://a.com"),
            title="t",
            content="c",
            content_hash="h",
        )
        data = d.model_dump_json()
        restored = ScrapedDocument.model_validate_json(data)
        assert restored.source_id == d.source_id
        assert restored.content_hash == d.content_hash
