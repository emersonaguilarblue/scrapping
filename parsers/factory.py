from src.core.enums import ScrapeStrategy
from src.core.exceptions import ParserError
from src.parsers.base_parser import BaseParser
from src.parsers.html_parser import HtmlParser
from src.parsers.litho_parser import LithoApiParser
from src.parsers.pdf_parser import PdfParser


class ParserFactory:
    def __init__(self) -> None:
        self._registry: dict[ScrapeStrategy, BaseParser] = {
            ScrapeStrategy.STATIC: HtmlParser(),
            ScrapeStrategy.DYNAMIC: HtmlParser(),
            ScrapeStrategy.PDF: PdfParser(),
            ScrapeStrategy.LITHO_API: LithoApiParser(),
        }

    def get(self, strategy: ScrapeStrategy) -> BaseParser:
        try:
            return self._registry[strategy]
        except KeyError as exc:
            raise ParserError(f"No parser registered for {strategy}") from exc
