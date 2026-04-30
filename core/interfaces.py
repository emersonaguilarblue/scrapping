from abc import ABC, abstractmethod

from src.core.models import PageSource, RawPayload, ScrapedDocument


class IScraper(ABC):
    @abstractmethod
    async def fetch(self, source: PageSource) -> RawPayload: ...


class IParser(ABC):
    @abstractmethod
    def parse(self, source: PageSource, payload: RawPayload) -> ScrapedDocument: ...


class IStorage(ABC):
    @abstractmethod
    def save(self, document: ScrapedDocument) -> None: ...

    @abstractmethod
    def save_raw(self, payload: RawPayload) -> None: ...


class ICache(ABC):
    @abstractmethod
    def get(self, key: str) -> RawPayload | None: ...

    @abstractmethod
    def set(self, key: str, payload: RawPayload) -> None: ...
