from abc import abstractmethod

from src.core.interfaces import IParser
from src.core.models import PageSource, RawPayload, ScrapedDocument


class BaseParser(IParser):
    @abstractmethod
    def parse(self, source: PageSource, payload: RawPayload) -> ScrapedDocument: ...
