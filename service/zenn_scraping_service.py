from playwright.async_api import async_playwright

from interface.i_scraping_service import IScrapingService

BODY_MAX_LENGTH = 100_000
ZENN_ARTICLE_SELECTOR = ".znc"


class ZennScrapingService(IScrapingService):
    async def fetch_body(self, url: str) -> str:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            try:
                page = await browser.new_page()
                await page.goto(url)
                element = await page.query_selector(ZENN_ARTICLE_SELECTOR)
                if element is None:
                    return ""
                text = await element.inner_text()
                return text[:BODY_MAX_LENGTH]
            finally:
                await browser.close()
