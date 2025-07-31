import json
import os
from typing import Dict, Any
from tools.logger import setup_logger

logger = setup_logger()

class ConfigLoader:
    def load_ui_config(self) -> Dict[str, Any]:
        try:
            with open(os.path.join("data", "ui_flow_config.json"), "r", encoding="utf-8") as f:
                config: Dict[str, Any] = json.load(f)
            if "yourapp.com" in config.get("url", ""):
                logger.warning("Placeholder URL detected in ui_flow_config.json. Please update to a valid URL for production use.")
            autocrawl = config.get("autocrawl", False)
            if not isinstance(autocrawl, (bool, int)):
                logger.warning("Invalid 'autocrawl' value in ui_flow_config.json. Defaulting to false.")
                config["autocrawl"] = False
            elif isinstance(autocrawl, int) and autocrawl < 1:
                logger.warning("Invalid 'autocrawl' depth. Defaulting to false.")
                config["autocrawl"] = False
            logger.info("UI config loaded successfully")
            return config
        except Exception as e:
            logger.error(f"Error loading UI config: {str(e)}")
            raise