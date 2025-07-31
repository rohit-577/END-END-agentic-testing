import asyncio
import json
import os
from crewmaster import CrewMaster
from tools.config_loader import ConfigLoader
from tools.logger import setup_logger
from typing import Dict, Any

logger = setup_logger()

async def main() -> None:
    try:
        logger.info("Starting autotest_agent")
        config_loader = ConfigLoader()
        ui_config: Dict[str, Any] = config_loader.load_ui_config()
        pr_diff: Dict[str, Any] = {}
        if os.path.exists("pr_diff.json"):
            with open("pr_diff.json", "r", encoding="utf-8") as f:
                pr_diff = json.load(f)
        logger.debug(f"Loaded UI config: {ui_config}, PR diff: {pr_diff}")
        crew_master = CrewMaster(ui_config, pr_diff)
        await crew_master.run()
        logger.info("autotest_agent completed successfully")
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())