from tools.logger import setup_logger
import time

logger = setup_logger()

class RetryHandler:
    def __init__(self, max_retries=3, delay=1):
        self.max_retries = max_retries
        self.delay = delay

    def retry(self, func):
        async def wrapper(*args, **kwargs):
            for attempt in range(self.max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                    if attempt == self.max_retries - 1:
                        logger.error(f"Max retries reached for {func.__name__}")
                        raise
                    time.sleep(self.delay)
        return wrapper