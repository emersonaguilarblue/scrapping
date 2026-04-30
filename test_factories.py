"""Pruebas para src.parsers.factory y src.scrapers.factory."""
import pytest

from src.config.settings import Settings
from src.core.enums import ScrapeStrategy
from src.core.exceptions import ParserError, ScraperError
from src.parsers.base_parser import BaseParser
from src.parsers.factory import ParserFactory
from src.parsers.html_parser import HtmlParser
from src.parsers.litho_parser import LithoApiParser
from src.parsers.pdf_parser import PdfParser
from src.scrapers.base import BaseScraper
from src.scrapers.factory import ScraperFactory


class TestParserFactory:
    def test_returns_html_parser_for_static(self) -> None:
        f = ParserFactory()
        assert isinstance(f.get(ScrapeStrategy.STATIC), HtmlParser)

    def test_returns_html_parser_for_dynamic(self) -> None:
        f = ParserFactory()
        assert isinstance(f.get(ScrapeStrategy.DYNAMIC), HtmlParser)

    def test_returns_pdf_parser(self) -> None:
        f = ParserFactory()
        assert isinstance(f.get(ScrapeStrategy.PDF), PdfParser)

    def test_returns_litho_parser(self) -> None:
        f = ParserFactory()
        assert isinstance(f.get(ScrapeStrategy.LITHO_API), LithoApiParser)

    def test_all_parsers_extend_base(self) -> None:
        f = ParserFactory()
        for strat in ScrapeStrategy:
            assert isinstance(f.get(strat), BaseParser)

    def test_caches_instances(self) -> None:
        f = ParserFactory()
        assert f.get(ScrapeStrategy.STATIC) is f.get(ScrapeStrategy.STATIC)


class TestScraperFactory:
    def test_all_strategies_resolve(self, settings: Settings) -> None:
        f = ScraperFactory(settings)
        for strat in ScrapeStrategy:
            assert isinstance(f.get(strat), BaseScraper)

    def test_caches_instances(self, settings: Settings) -> None:
        f = ScraperFactory(settings)
        assert f.get(ScrapeStrategy.STATIC) is f.get(ScrapeStrategy.STATIC)


class TestFactoriesErrors:
    def test_parser_factory_raises_for_unknown(self) -> None:
        f = ParserFactory()
        # Forzamos un valor no registrado limpiando registry
        f._registry.clear()
        with pytest.raises(ParserError):
            f.get(ScrapeStrategy.STATIC)

    def test_scraper_factory_raises_for_unknown(self, settings: Settings) -> None:
        f = ScraperFactory(settings)
        f._registry.clear()
        with pytest.raises(ScraperError):
            f.get(ScrapeStrategy.STATIC)
