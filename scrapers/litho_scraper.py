import asyncio
import json

from loguru import logger
from playwright.async_api import async_playwright
from tenacity import retry, stop_after_attempt, wait_exponential

from src.core.exceptions import ScraperError
from src.core.models import PageSource, RawPayload
from src.scrapers.base import BaseScraper

_LITHO_HOST = "litho.silvercloudinc.com"
_LITHO_PATH = "/kb/content/integration_procedures/"


class LithoApiScraper(BaseScraper):
    """
    Fetches Claro FAQ content by intercepting the SilverCloud XHR call
    made while the browser renders the FAQ page.
    """

    async def fetch(self, source: PageSource) -> RawPayload:
        return await self._fetch_with_retry(source)

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=15),
    )
    async def _fetch_with_retry(self, source: PageSource) -> RawPayload:
        procedure_id = source.extra.get("procedure_id")
        if not procedure_id:
            raise ScraperError(
                f"[litho_api] source '{source.id}' missing extra.procedure_id"
            )

        url = str(source.url)
        logger.info(f"[litho_api] loading {url} to intercept XHR for {procedure_id}")

        captured: dict = {}

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=self.settings.headless)
            try:
                context = await browser.new_context(
                    user_agent=self.settings.user_agent,
                    locale=self.settings.locale,
                    timezone_id=self.settings.timezone,
                    viewport={"width": 1366, "height": 900},
                )
                page = await context.new_page()
                page.set_default_timeout(self.settings.timeout_ms)

                async def handle_response(response):
                    if (
                        _LITHO_HOST in response.url
                        and _LITHO_PATH in response.url
                        and procedure_id in response.url
                        and response.status == 200
                    ):
                        try:
                            body = await response.body()
                            data = json.loads(body)
                            captured["json"] = data
                            captured["url"] = response.url
                            logger.info(
                                f"[litho_api] captured XHR for {source.id}: "
                                f"{len(data.get('steps', []))} steps"
                            )
                        except Exception as exc:
                            logger.warning(f"[litho_api] XHR capture failed: {exc}")

                page.on("response", handle_response)

                await page.goto(url, wait_until=self.settings.nav_wait)

                for _ in range(30):
                    if "json" in captured:
                        break
                    await asyncio.sleep(0.5)

            finally:
                await browser.close()

        if "json" not in captured:
            raise ScraperError(
                f"[litho_api] XHR for {procedure_id} not captured on {url} "
                f"(page may not have loaded the widget)"
            )

        return RawPayload(
            source_id=source.id,
            url=source.url,
            content_type="application/json",
            body=json.dumps(captured["json"]).encode("utf-8"),
            status_code=200,
            final_url=captured.get("url", url),
        )
