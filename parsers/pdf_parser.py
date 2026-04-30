from io import BytesIO

import pdfplumber

from src.core.exceptions import ParserError
from src.core.models import PageSource, RawPayload, ScrapedDocument
from src.parsers.base_parser import BaseParser
from src.pipeline.hashing import compute_hash
from src.pipeline.normalizer import normalize_text


class PdfParser(BaseParser):
    def parse(self, source: PageSource, payload: RawPayload) -> ScrapedDocument:
        try:
            with pdfplumber.open(BytesIO(payload.body)) as pdf:
                pages = [page.extract_text() or "" for page in pdf.pages]
                num_pages = len(pdf.pages)
        except Exception as exc:
            raise ParserError(f"Cannot read PDF for {source.id}: {exc}") from exc

        raw = "\n\n".join(p for p in pages if p)
        clean = normalize_text(raw)

        if not clean:
            raise ParserError(f"Empty PDF content for {source.id}")

        md_parts: list[str] = [f"# {source.name}"]
        for idx, page_text in enumerate(pages, start=1):
            page_clean = normalize_text(page_text)
            if not page_clean:
                continue
            md_parts.append(f"## Página {idx}")
            md_parts.append(page_clean)
        markdown = "\n\n".join(md_parts).strip()

        return ScrapedDocument(
            source_id=source.id,
            url=payload.url,
            title=source.name,
            content=clean,
            markdown=markdown,
            metadata={
                "category": source.category.value,
                "strategy": source.strategy.value,
                "breadcrumb": source.breadcrumb,
                "final_url": str(payload.final_url) if payload.final_url else None,
                "num_pages": num_pages,
                "content_length": len(clean),
                "markdown_length": len(markdown),
            },
            content_hash=compute_hash(clean),
        )
