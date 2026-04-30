"""Pruebas para src.parsers.litho_parser (módulo independiente, sin red)."""
import json

import pytest
from pydantic import HttpUrl

from src.core.enums import ScrapeStrategy, SourceCategory
from src.core.exceptions import ParserError
from src.core.models import PageSource, RawPayload
from src.parsers.litho_parser import LithoApiParser, _clean_title, _strip_html


class TestStripHtml:
    def test_empty_returns_empty(self) -> None:
        assert _strip_html("") == ""

    def test_removes_tags(self) -> None:
        assert _strip_html("<p>hola</p>") == "hola"

    def test_converts_br_to_newline(self) -> None:
        out = _strip_html("a<br>b<br/>c")
        assert "a" in out and "b" in out and "c" in out
        assert "<" not in out

    def test_unescapes_entities(self) -> None:
        assert _strip_html("&amp; &lt;") == "& <"

    def test_collapses_whitespace(self) -> None:
        assert "  " not in _strip_html("<p>a   b</p>")


class TestCleanTitle:
    def test_removes_html(self) -> None:
        assert _clean_title("<b1>Trámites hogar") == "Trámites hogar"

    def test_strips_whitespace(self) -> None:
        assert _clean_title("  hola  ") == "hola"


class TestLithoParserParse:
    def _payload(self, body: dict, url: str = "https://api.example.com/p?procid=1") -> RawPayload:
        return RawPayload(
            source_id="t",
            url=HttpUrl(url),
            content_type="application/json",
            body=json.dumps(body).encode("utf-8"),
        )

    def _source(self) -> PageSource:
        return PageSource(
            id="t",
            name="Tramite",
            url=HttpUrl("https://api.example.com/p?procid=1"),
            category=SourceCategory.OTROS,
            strategy=ScrapeStrategy.LITHO_API,
        )

    def test_parses_minimal_steps(self) -> None:
        payload = self._payload({
            "title": "Procedimiento X",
            "steps": [{"id": "s1", "title": "Paso 1", "body": "<p>Hola</p>", "published": True}],
        })
        doc = LithoApiParser().parse(self._source(), payload)
        assert "Hola" in doc.content
        assert doc.metadata["num_steps"] == 1
        assert doc.content_hash

    def test_raises_on_invalid_json(self) -> None:
        payload = RawPayload(
            source_id="t",
            url=HttpUrl("https://api.example.com/p"),
            content_type="application/json",
            body=b"not json{",
        )
        with pytest.raises(ParserError):
            LithoApiParser().parse(self._source(), payload)

    def test_raises_on_no_steps(self) -> None:
        payload = self._payload({"title": "X", "steps": []})
        with pytest.raises(ParserError):
            LithoApiParser().parse(self._source(), payload)

    def test_filters_unpublished_steps(self) -> None:
        payload = self._payload({
            "title": "X",
            "steps": [
                {"id": "s1", "title": "P1", "body": "Hola", "published": True},
                {"id": "s2", "title": "P2", "body": "Mundo", "published": False},
            ],
        })
        doc = LithoApiParser().parse(self._source(), payload)
        assert "Hola" in doc.content
        assert "Mundo" not in doc.content

    def test_filters_by_step_id(self) -> None:
        url = "https://api.example.com/p?procid=1&stepId=s2"
        payload = self._payload({
            "title": "X",
            "steps": [
                {"id": "s1", "title": "P1", "body": "AAA", "published": True},
                {"id": "s2", "title": "P2", "body": "BBB", "published": True},
            ],
        }, url=url)
        src = PageSource(
            id="t",
            name="T",
            url=HttpUrl(url),
            category=SourceCategory.OTROS,
            strategy=ScrapeStrategy.LITHO_API,
        )
        doc = LithoApiParser().parse(src, payload)
        assert "BBB" in doc.content
        assert "AAA" not in doc.content
