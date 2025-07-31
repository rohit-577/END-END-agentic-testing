from tools.playwright_executor import PlaywrightExecutor
from tools.screenshot_diff import ScreenshotDiff
from tools.logger import setup_logger
from tasks import UIAgentOutput, UITestFlow
import json
import os
from typing import Dict, Any, List, TextIO, Optional, TypedDict

logger = setup_logger()

# Define structure for ui_config["flows"][0]
class FlowConfig(TypedDict):
    page: str
    actions: List[Dict[str, Any]]
    expected_result: Dict[str, str]
    reference_screenshot: Optional[str]

class UIAgent:
    def __init__(self, ui_config: Dict[str, Any]):
        self.ui_config: Dict[str, Any] = ui_config
        self.playwright_executor = PlaywrightExecutor(ui_config)
        self.screenshot_diff = ScreenshotDiff()
        self.screenshots_file: str = os.path.join("results", "screenshots", "screenshots.json")

    async def execute_ui_flow(self) -> UIAgentOutput:
        try:
            os.makedirs(os.path.dirname(self.screenshots_file), exist_ok=True)
            ui_test_flows: List[UITestFlow] = []
            screenshot_paths: List[str] = []

            if "yourapp.com" in self.ui_config.get("url", ""):
                logger.warning("Placeholder URL detected. Running in test mode with mock outputs.")
                ui_test_flows = [
                    UITestFlow(
                        name=f"Mock Test {i}",
                        steps=[f"Click mock_selector_{i}"],
                        success_criteria="Mocked success",
                        screenshots=[f"results/screenshots/mock_screenshot_{i}.png"]
                    ) for i in range(1, 3)
                ]
                screenshot_paths = [f"results/screenshots/mock_screenshot_{i}.png" for i in range(1, 3)]
                with open(self.screenshots_file, "w", encoding="utf-8") as f:  # type
                    json.dump({"screenshots": screenshot_paths}, f, indent=2)
                return UIAgentOutput(
                    ui_test_flows=ui_test_flows,
                    screenshot_diffs=[],
                    login_status="mocked",
                    generated_test_file=os.path.join("tests", "ui", "test_ui.py"),
                    results_file=os.path.join("results", "test_logs", "results.json"),
                    screenshots_file=self.screenshots_file
                )

            if self.ui_config.get("autocrawl", False):
                depth: int = self.ui_config.get("autocrawl", 2) if isinstance(self.ui_config.get("autocrawl"), int) else 2
                logger.info(f"Executing autocrawl with depth {depth}")
                crawl_results: List[Dict[str, Any]] = await self.playwright_executor.crawl(depth)
                for i, result in enumerate(crawl_results):  # type
                    test_id: str = f"ui_crawl_{i+1}"
                    screenshot_path: str = os.path.join("results", "screenshots", f"{test_id}_step_1.png")
                    await self.playwright_executor.take_screenshot(screenshot_path)
                    passed: bool = self.screenshot_diff.compare(screenshot_path, result.get("reference_screenshot", ""))
                    ui_test_flows.append(UITestFlow(
                        name=f"Crawl Test {test_id}",
                        steps=[json.dumps(action) for action in result.get("actions", [])],
                        success_criteria=json.dumps(result.get("expected_result", {})),
                        screenshots=[screenshot_path]
                    ))
                    screenshot_paths.append(screenshot_path)
            else:
                for flow in self.ui_config.get("flows", []):  # type
                    test_id: str = f"ui_{flow.get('page', 'unknown')}_{flow.get('actions', [{}])[0].get('type', 'unknown')}"
                    result: Dict[str, Any] = await self.playwright_executor.execute_flow(flow)
                    screenshot_path: str = os.path.join("results", "screenshots", f"{test_id}_step_1.png")
                    await self.playwright_executor.take_screenshot(screenshot_path)
                    passed: bool = self.screenshot_diff.compare(screenshot_path, flow.get("reference_screenshot", ""))
                    ui_test_flows.append(UITestFlow(
                        name=f"Test for {flow.get('page', 'unknown')}",
                        steps=[json.dumps(action) for action in flow.get("actions", [])],
                        success_criteria=json.dumps(flow.get("expected_result", {})),
                        screenshots=[screenshot_path]
                    ))
                    screenshot_paths.append(screenshot_path)

            with open(self.screenshots_file, "w", encoding="utf-8") as f:  # type
                json.dump({"screenshots": screenshot_paths}, f, indent=2)
            logger.info("UI flow execution completed: %s", ui_test_flows)
            return UIAgentOutput(
                ui_test_flows=ui_test_flows,
                screenshot_diffs=[],
                login_status="completed",
                generated_test_file=os.path.join("tests", "ui", "test_ui.py"),
                results_file=os.path.join("results", "test_logs", "results.json"),
                screenshots_file=self.screenshots_file
            )
        except Exception as e:
            logger.error(f"Error executing UI flow: {str(e)}")
            raise