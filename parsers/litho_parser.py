import html as _html
import json
import re
from urllib.parse import parse_qs, urlparse

from src.core.exceptions import ParserError
from src.core.models import PageSource, RawPayload, ScrapedDocument
from src.parsers.base_parser import BaseParser
from src.pipeline.hashing import compute_hash
from src.pipeline.normalizer import normalize_text


def _strip_html(html: str) -> str:
    if not html:
        return ""
    html = re.sub(r"<br\s*/?>", "\n", html, flags=re.IGNORECASE)
    html = re.sub(r"</p\s*>", "\n", html, flags=re.IGNORECASE)
    html = re.sub(r"</h[1-6]\s*>", "\n", html, flags=re.IGNORECASE)
    html = re.sub(r"<li[^>]*>", "- ", html, flags=re.IGNORECASE)
    html = re.sub(r"</li\s*>", "\n", html, flags=re.IGNORECASE)
    html = re.sub(r"</(ol|ul)\s*>", "\n", html, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", html)
    text = _html.unescape(text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _html_to_markdown(raw: str) -> str:
    """Convert step body HTML to Markdown preserving headings, lists, links and emphasis."""
    if not raw:
        return ""

    html = raw
    # Normalize block transitions
    html = re.sub(r"<br\s*/?>", "\n", html, flags=re.IGNORECASE)
    # Headings
    for level in range(1, 7):
        prefix = "#" * level
        html = re.sub(
            rf"<h{level}[^>]*>(.*?)</h{level}\s*>",
            lambda m, p=prefix: f"\n\n{p} {m.group(1).strip()}\n\n",
            html,
            flags=re.IGNORECASE | re.DOTALL,
        )
    # Bold / italic
    html = re.sub(r"<(b|strong)[^>]*>(.*?)</\1\s*>", r"**\2**", html, flags=re.IGNORECASE | re.DOTALL)
    html = re.sub(r"<(i|em)[^>]*>(.*?)</\1\s*>", r"*\2*", html, flags=re.IGNORECASE | re.DOTALL)
    # Links
    html = re.sub(
        r"<a[^>]*href=[\"']([^\"']+)[\"'][^>]*>(.*?)</a\s*>",
        lambda m: f"[{re.sub(r'<[^>]+>', '', m.group(2)).strip()}]({m.group(1)})",
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    # Lists
    html = re.sub(r"<li[^>]*>", "- ", html, flags=re.IGNORECASE)
    html = re.sub(r"</li\s*>", "\n", html, flags=re.IGNORECASE)
    html = re.sub(r"</?(ul|ol)\s*[^>]*>", "\n", html, flags=re.IGNORECASE)
    # Paragraphs
    html = re.sub(r"</p\s*>", "\n\n", html, flags=re.IGNORECASE)
    html = re.sub(r"<p[^>]*>", "", html, flags=re.IGNORECASE)
    # Drop remaining tags
    text = re.sub(r"<[^>]+>", "", html)
    text = _html.unescape(text)
    # Whitespace cleanup
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _clean_title(raw: str) -> str:
    """Remove HTML tags from titles like '<b1>Trámites hogar'."""
    return re.sub(r"<[^>]+>", "", raw).strip()


class LithoApiParser(BaseParser):
    """Parses SilverCloud/Litho API JSON into a ScrapedDocument."""

    def parse(self, source: PageSource, payload: RawPayload) -> ScrapedDocument:
        try:
            data = json.loads(payload.body)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ParserError(f"[litho] Cannot decode JSON for {source.id}") from exc

        procedure_title = _clean_title(data.get("title") or source.name)
        steps: list[dict] = data.get("steps") or []

        if not steps:
            raise ParserError(f"[litho] No steps found for {source.id}")

        parsed_url = urlparse(str(payload.url))
        step_id = parse_qs(parsed_url.query).get("stepId", [None])[0]
        if step_id:
            steps = [s for s in steps if s.get("id") == step_id]
            if not steps:
                raise ParserError(
                    f"[litho] step_id '{step_id}' not found in procedure {source.id}"
                )

        parts: list[str] = []
        md_parts: list[str] = [f"# {procedure_title}"]

        for step in steps:
            if not step.get("published", True):
                continue

            step_title = step.get("title", "").strip()
            raw_body = step.get("body", "")
            step_body_text = _strip_html(raw_body)
            step_body_md = _html_to_markdown(raw_body)

            if step_title:
                parts.append(f"## {step_title}")
                md_parts.append(f"## {step_title}")
            if step_body_text:
                parts.append(step_body_text)
            if step_body_md:
                md_parts.append(step_body_md)

        title = steps[0].get("title", procedure_title).strip() if steps else procedure_title

        content = normalize_text("\n".join(parts))
        markdown = re.sub(r"\n{3,}", "\n\n", "\n\n".join(md_parts)).strip()

        if not content:
            raise ParserError(f"[litho] Empty content after parsing for {source.id}")

        return ScrapedDocument(
            source_id=source.id,
            url=payload.url,
            title=title,
            content=content,
            markdown=markdown,
            metadata={
                "category": source.category.value,
                "strategy": source.strategy.value,
                "breadcrumb": source.breadcrumb,
                "procedure_title": procedure_title,
                "num_steps": len(steps),
                "content_length": len(content),
                "markdown_length": len(markdown),
            },
            content_hash=compute_hash(content),
        )
