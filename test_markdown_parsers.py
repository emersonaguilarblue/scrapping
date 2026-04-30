"""Pruebas de extracción a Markdown en parsers."""
import json

import pytest
from pydantic import HttpUrl

from src.core.enums import ScrapeStrategy, SourceCategory
from src.core.models import PageSource, RawPayload
from src.parsers.litho_parser import LithoApiParser, _html_to_markdown


class TestHtmlToMarkdown:
    def test_empty(self) -> None:
        assert _html_to_markdown("") == ""

    def test_headings(self) -> None:
        out = _html_to_markdown("<h1>Tit</h1><h2>Sub</h2>")
        assert "# Tit" in out
        assert "## Sub" in out

    def test_bold_and_italic(self) -> None:
        out = _html_to_markdown("<b>fuerte</b> y <i>cursiva</i>")
        assert "**fuerte**" in out
        assert "*cursiva*" in out

    def test_links(self) -> None:
        out = _html_to_markdown('<a href="https://x.co">click</a>')
        assert "[click](https://x.co)" in out

    def test_lists(self) -> None:
        out = _html_to_markdown("<ul><li>uno</li><li>dos</li></ul>")
        assert "- uno" in out
        assert "- dos" in out

    def test_paragraphs(self) -> None:
        out = _html_to_markdown("<p>uno</p><p>dos</p>")
        assert "uno" in out and "dos" in out


class TestLithoMarkdownOutput:
    def _payload(self, body: dict) -> RawPayload:
        return RawPayload(
            source_id="t",
            url=HttpUrl("https://api.example.com/p?procid=1"),
            content_type="application/json",
            body=json.dumps(body).encode("utf-8"),
        )

    def _source(self) -> PageSource:
        return PageSource(
            id="t",
            name="T",
            url=HttpUrl("https://api.example.com/p?procid=1"),
            category=SourceCategory.OTROS,
            strategy=ScrapeStrategy.LITHO_API,
        )

    def test_markdown_field_populated(self) -> None:
        payload = self._payload({
            "title": "Procedimiento X",
            "steps": [
                {
                    "id": "s1",
                    "title": "Paso 1",
                    "body": "<p><b>Hola</b> mundo</p><ul><li>a</li><li>b</li></ul>",
                    "published": True,
                }
            ],
        })
        doc = LithoApiParser().parse(self._source(), payload)
        assert doc.markdown
        assert "# Procedimiento X" in doc.markdown
        assert "## Paso 1" in doc.markdown
        assert "**Hola**" in doc.markdown
        assert "- a" in doc.markdown
        assert "- b" in doc.markdown

    def test_metadata_includes_markdown_length(self) -> None:
        payload = self._payload({
            "title": "X",
            "steps": [{"id": "s1", "title": "P", "body": "<p>hi</p>", "published": True}],
        })
        doc = LithoApiParser().parse(self._source(), payload)
        assert "markdown_length" in doc.metadata
        assert doc.metadata["markdown_length"] > 0
