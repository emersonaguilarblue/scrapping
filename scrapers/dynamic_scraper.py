import asyncio

from loguru import logger
from playwright.async_api import async_playwright
from tenacity import retry, stop_after_attempt, wait_exponential

from src.core.exceptions import ScraperError
from src.core.models import PageSource, RawPayload
from src.scrapers.base import BaseScraper


class DynamicScraper(BaseScraper):
    async def fetch(self, source: PageSource) -> RawPayload:
        return await self._fetch_with_retry(source)

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=15),
    )
    async def _fetch_with_retry(self, source: PageSource) -> RawPayload:
        url = str(source.url)
        logger.info(f"[dynamic] GET {url}")

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

                response = await page.goto(url, wait_until=self.settings.nav_wait)
                if response is None:
                    raise ScraperError(f"No response from {url}")

                if source.wait_selector:
                    try:
                        await page.wait_for_selector(
                            source.wait_selector,
                            timeout=self.settings.timeout_ms,
                        )
                    except Exception as exc:
                        logger.warning(f"wait_selector miss for {source.id}: {exc}")

                dismissed = await self._dismiss_cookie_banner(page)
                if dismissed:
                    try:
                        await page.wait_for_load_state("networkidle", timeout=8000)
                    except Exception:
                        await asyncio.sleep(1)

                html = await page.content()
                final_url = page.url
                status = response.status

                return RawPayload(
                    source_id=source.id,
                    url=source.url,
                    content_type="text/html",
                    body=html.encode("utf-8"),
                    status_code=status,
                    final_url=final_url,
                )
            finally:
                await browser.close()

    @staticmethod
    async def _dismiss_cookie_banner(page) -> bool:
        selectors = (
            "#onetrust-accept-btn-handler",
            "button:has-text('Aceptar')",
            "button:has-text('Acepto')",
        )
        for sel in selectors:
            try:
                btn = await page.query_selector(sel)
                if btn:
                    await btn.click(timeout=2000)
                    return True
            except Exception:
                continue
        return False
