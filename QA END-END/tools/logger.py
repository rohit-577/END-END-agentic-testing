import logging
import os
from datetime import datetime

def setup_logger() -> logging.Logger:
    logger = logging.getLogger("autotest_agent")
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)  # Set to DEBUG for detailed tracing
        os.makedirs("logs", exist_ok=True)  # Create logs directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        handler = logging.FileHandler(f"logs/autotest_log_{timestamp}.log")
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        # Add console handler for immediate feedback
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    return logger