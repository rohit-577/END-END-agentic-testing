from playwright.async_api import async_playwright
from tools.logger import setup_logger
from tools.retry_handler import RetryHandler

logger = setup_logger()
retry_handler = RetryHandler()

class PlaywrightExecutor:
    def __init__(self, ui_config):
        self.ui_config = ui_config

    @retry_handler.retry
    async def execute_flow(self, flow):
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()
                if "yourapp.com" in self.ui_config.get("url", ""):
                    logger.warning("Placeholder URL detected. Using mock execution.")
                    return {"status": "mocked"}
                
                await page.goto(self.ui_config["url"])
                for action in flow["actions"]:
                    if action["type"] == "click":
                        await page.click(action["selector"])
                    elif action["type"] == "fill":
                        await page.fill(action["selector"], action["value"])
                result = {"status": "completed"}
                await browser.close()
                return result
        except Exception as e:
            logger.error(f"Error executing Playwright flow: {str(e)}")
            raise

    @retry_handler.retry
    async def take_screenshot(self, path):
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()
                if "yourapp.com" in self.ui_config.get("url", ""):
                    logger.warning("Placeholder URL detected. Saving mock screenshot.")
                    with open(path, "w") as f:
                        f.write("Mock screenshot")
                    return
                await page.goto(self.ui_config["url"])
                await page.screenshot(path=path)
                await browser.close()
                logger.info(f"Screenshot saved at {path}")
        except Exception as e:
            logger.error(f"Error taking screenshot: {str(e)}")
            raise

    @retry_handler.retry
    async def crawl(self, max_depth):
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()
                if "yourapp.com" in self.ui_config.get("url", ""):
                    logger.warning("Placeholder URL detected. Using mock crawl.")
                    return [
                        {
                            "page": f"mock_page_{i}",
                            "actions": [{"type": "click", "selector": f"mock_selector_{i}"}],
                            "expected_result": {"status": "mocked"}
                        } for i in range(1, 3)
                    ]
                
                results = []
                visited = set()
                queue = [(self.ui_config["url"], [], 0)]
                
                while queue and len(results) < 10:  # Limit to 10 pages for performance
                    url, actions, depth = queue.pop(0)
                    if url in visited or depth > max_depth:
                        continue
                    visited.add(url)
                    
                    try:
                        await page.goto(url, timeout=10000)
                        elements = await page.query_selector_all("a, button")
                        for element in elements[:3]:  # Limit to 3 elements per page
                            selector = await element.get_attribute("id") or await element.get_attribute("class") or "unknown"
                            results.append({
                                "page": url,
                                "actions": actions + [{"type": "click", "selector": selector}],
                                "expected_result": {"status": "navigated"}
                            })
                            href = await element.get_attribute("href")
                            if href and depth + 1 <= max_depth:
                                queue.append((href, actions + [{"type": "click", "selector": selector}], depth + 1))
                    except Exception as e:
                        logger.warning(f"Error crawling {url}: {str(e)}")
                
                await browser.close()
                logger.info(f"Crawl completed, found {len(results)} pages")
                return results
        except Exception as e:
            logger.error(f"Error in crawl: {str(e)}")
            raise