import trafilatura
from selectolax.parser import HTMLParser

from src.config.constants import REMOVABLE_SELECTORS
from src.core.exceptions import ParserError
from src.core.models import PageSource, RawPayload, ScrapedDocument
from src.parsers.base_parser import BaseParser
from src.pipeline.hashing import compute_hash
from src.pipeline.normalizer import normalize_text


class HtmlParser(BaseParser):
    def parse(self, source: PageSource, payload: RawPayload) -> ScrapedDocument:
        try:
            html = payload.body.decode("utf-8", errors="ignore")
        except Exception as exc:
            raise ParserError(f"Cannot decode body for {source.id}") from exc

        title = self._extract_title(html) or source.name
        content = self._extract_content(html, str(payload.url))
        markdown = self._extract_markdown(html, str(payload.url))
        clean = normalize_text(content)
        markdown_clean = self._normalize_markdown(markdown) if markdown else clean

        if not clean:
            raise ParserError(f"Empty content for {source.id}")

        if len(clean) < 600 and "nuestro sitio web utiliza cookies" in clean:
            raise ParserError(
                f"Only cookie-banner content extracted for {source.id} — "
                "add a wait_selector or switch strategy"
            )

        return ScrapedDocument(
            source_id=source.id,
            url=payload.url,
            title=title,
            content=clean,
            markdown=markdown_clean,
            metadata={
                "category": source.category.value,
                "strategy": source.strategy.value,
                "breadcrumb": source.breadcrumb,
                "final_url": str(payload.final_url) if payload.final_url else None,
                "status_code": payload.status_code,
                "content_length": len(clean),
                "markdown_length": len(markdown_clean),
            },
            content_hash=compute_hash(clean),
        )

    @staticmethod
    def _extract_title(html: str) -> str | None:
        tree = HTMLParser(html)
        node = tree.css_first("title")
        return node.text(strip=True) if node else None

    @staticmethod
    def _extract_content(html: str, url: str) -> str:
        clean_html = HtmlParser._strip_before_parse(html)

        extracted = trafilatura.extract(
            clean_html,
            url=url,
            include_comments=False,
            include_tables=True,
            include_links=False,
            favor_precision=True,
        )
        if extracted and len(extracted) >= 400:
            return extracted
        fallback = HtmlParser._fallback_extract(html)
        return fallback if fallback else (extracted or "")

    @staticmethod
    def _extract_markdown(html: str, url: str) -> str:
        """Extract main content as Markdown preserving structure (headings, lists, tables, links)."""
        clean_html = HtmlParser._strip_before_parse(html)
        extracted = trafilatura.extract(
            clean_html,
            url=url,
            include_comments=False,
            include_tables=True,
            include_links=True,
            include_formatting=True,
            favor_precision=True,
            output_format="markdown",
        )
        return extracted or ""

    @staticmethod
    def _normalize_markdown(md: str) -> str:
        """Light normalization that preserves Markdown syntax."""
        import re

        md = md.replace("\r\n", "\n").replace("\r", "\n")
        md = re.sub(r"[ \t]+\n", "\n", md)
        md = re.sub(r"\n{3,}", "\n\n", md)
        return md.strip()

    @staticmethod
    def _strip_before_parse(html: str) -> str:
        """Remove known noise elements before passing HTML to trafilatura."""
        noise = (
            "#onetrust-banner-sdk",
            "#onetrust-consent-sdk",
            ".cookie",
            ".cookies",
            "[class*='cookie']",
            "[id*='cookie']",
            "[class*='consent']",
            "[id*='consent']",
            "script",
            "style",
            "noscript",
        )
        tree = HTMLParser(html)
        for sel in noise:
            for node in tree.css(sel):
                node.decompose()
        return tree.html or html

    @staticmethod
    def _fallback_extract(html: str) -> str:
        tree = HTMLParser(html)
        for sel in REMOVABLE_SELECTORS:
            for node in tree.css(sel):
                node.decompose()
        body = tree.body
        return body.text(separator="\n", strip=True) if body else ""
