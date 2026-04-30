from src.config.settings import Settings
from src.core.enums import ScrapeStrategy
from src.core.exceptions import ScraperError
from src.scrapers.base import BaseScraper
from src.scrapers.dynamic_scraper import DynamicScraper
from src.scrapers.litho_scraper import LithoApiScraper
from src.scrapers.pdf_scraper import PdfScraper
from src.scrapers.static_scraper import StaticScraper


class ScraperFactory:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._registry: dict[ScrapeStrategy, BaseScraper] = {
            ScrapeStrategy.STATIC: StaticScraper(settings),
            ScrapeStrategy.DYNAMIC: DynamicScraper(settings),
            ScrapeStrategy.PDF: PdfScraper(settings),
            ScrapeStrategy.LITHO_API: LithoApiScraper(settings),
        }

    def get(self, strategy: ScrapeStrategy) -> BaseScraper:
        try:
            return self._registry[strategy]
        except KeyError as exc:
            raise ScraperError(f"No scraper registered for {strategy}") from exc
