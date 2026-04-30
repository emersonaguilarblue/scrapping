import httpx
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config.constants import DEFAULT_HEADERS
from src.core.exceptions import ScraperError
from src.core.models import PageSource, RawPayload
from src.scrapers.base import BaseScraper


class PdfScraper(BaseScraper):
    async def fetch(self, source: PageSource) -> RawPayload:
        return await self._fetch_with_retry(source)

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
    )
    async def _fetch_with_retry(self, source: PageSource) -> RawPayload:
        headers = {**DEFAULT_HEADERS, "User-Agent": self.settings.user_agent}
        timeout = httpx.Timeout(self.settings.timeout_ms / 1000)
        url = str(source.url)

        logger.info(f"[pdf] GET {url}")
        async with httpx.AsyncClient(
            headers=headers,
            timeout=timeout,
            follow_redirects=True,
        ) as client:
            response = await client.get(url)
            if response.status_code >= 400:
                raise ScraperError(f"HTTP {response.status_code} for {url}")

            return RawPayload(
                source_id=source.id,
                url=source.url,
                content_type=response.headers.get("content-type", "application/pdf"),
                body=response.content,
                status_code=response.status_code,
                final_url=str(response.url),
            )
