from abc import abstractmethod

from src.config.settings import Settings
from src.core.interfaces import IScraper
from src.core.models import PageSource, RawPayload


class BaseScraper(IScraper):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    @abstractmethod
    async def fetch(self, source: PageSource) -> RawPayload: ...
