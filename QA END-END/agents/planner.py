from tools.llm import LLM
from tools.logger import setup_logger
from tasks import PlannerOutput, UITestFlow
import json
from typing import Dict, Any, List, Optional, TypedDict

logger = setup_logger()

# Define structure for actions in ui_config["flows"][0]["actions"]
class ActionConfig(TypedDict):
    type: str
    selector: str
    value: Optional[str]

# Define structure for expected_result
class ExpectedResult(TypedDict):
    url: str
    status: Optional[str]

# Define structure for ui_config["flows"][0]
class FlowConfig(TypedDict):
    page: str
    actions: List[ActionConfig]
    expected_result: ExpectedResult
    name: Optional[str]

# Define structure for test in test_plan
class TestConfig(TypedDict):
    test_id: str
    page: str
    actions: List[ActionConfig]
    expected_result: ExpectedResult
    name: str
    steps: List[ActionConfig]
    success_criteria: ExpectedResult

class Planner:
    def __init__(self, ui_config: Dict[str, Any], pr_diff: Dict[str, Any]):
        self.ui_config: Dict[str, Any] = ui_config
        self.pr_diff: Dict[str, Any] = pr_diff
        self.llm = LLM()

    def analyze_ui_config(self) -> Dict[str, List[TestConfig]]:
        try:
            test_plan: Dict[str, List[TestConfig]] = {"ui_tests": [], "unit_tests": [], "integration_tests": []}
            if self.ui_config.get("autocrawl", False):
                logger.info("Autocrawl enabled, UI tests will be generated dynamically")
                return test_plan
            default_action: ActionConfig = {"type": "unknown", "selector": "unknown", "value": None}
            default_expected: ExpectedResult = {"url": "", "status": "success"}
            for flow in self.ui_config.get("flows", []):  # type
                test_plan["ui_tests"].append({
                    "test_id": f"ui_{flow.get('page', 'unknown')}_{flow.get('actions', [default_action])[0].get('type', 'unknown')}",
                    "page": flow.get("page", "unknown"),
                    "actions": flow.get("actions", []),
                    "expected_result": flow.get("expected_result", default_expected),
                    "name": flow.get("name", f"Test for {flow.get('page', 'unknown')}"),
                    "steps": flow.get("actions", []),
                    "success_criteria": flow.get("expected_result", default_expected)
                })
            logger.info("UI config analysis completed")
            return test_plan
        except Exception as e:
            logger.error(f"Error analyzing UI config: {str(e)}")
            raise

    def analyze_diff(self) -> Dict[str, List[Dict[str, Any]]]:
        try:
            if not self.pr_diff:
                logger.info("No PR diff provided, skipping diff analysis")
                return {"unit_tests": [], "integration_tests": []}
            return {"unit_tests": [], "integration_tests": []}
        except Exception as e:
            logger.error(f"Error analyzing PR diff: {str(e)}")
            raise

    def merge_plans(self, ui_plan: Dict[str, List[Dict[str, Any]]], diff_plan: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        try:
            merged_plan: Dict[str, List[Dict[str, Any]]] = {
                "ui_tests": ui_plan.get("ui_tests", []),
                "unit_tests": ui_plan.get("unit_tests", []) + diff_plan.get("unit_tests", []),
                "integration_tests": ui_plan.get("integration_tests", []) + diff_plan.get("integration_tests", [])
            }
            return merged_plan
        except Exception as e:
            logger.error(f"Error merging plans: {str(e)}")
            raise

    def plan(self) -> PlannerOutput:
        try:
            ui_plan: Dict[str, List[Dict[str, Any]]] = self.analyze_ui_config()
            diff_plan: Dict[str, List[Dict[str, Any]]] = self.analyze_diff()
            test_plan: Dict[str, List[Dict[str, Any]]] = self.merge_plans(ui_plan, diff_plan)
            with open("plan.json", "w") as f:
                json.dump(test_plan, f, indent=2)
            default_expected: ExpectedResult = {"url": "", "status": "success"}
            output = PlannerOutput(
                test_plan=test_plan,
                unit_tests=[t.get("test_id", "unknown") for t in test_plan.get("unit_tests", [])],  # type: TestConfig
                integration_tests=[t.get("test_id", "unknown") for t in test_plan.get("integration_tests", [])],  # type: TestConfig
                ui_tests=[UITestFlow(
                    test_id=t.get("test_id", "unknown"),
                    name=t.get("name", "Unnamed Test"),
                    steps=[json.dumps(action) for action in t.get("steps", [])],
                    success_criteria=json.dumps(t.get("success_criteria", default_expected)),
                    page=t.get("page", "unknown"),
                    actions=t.get("actions", []),
                    expected_result=t.get("expected_result", default_expected)
                ) for t in test_plan.get("ui_tests", [])],  # type: TestConfig
                test_goals=["Ensure UI functionality", "Validate user interactions"],
                test_categories=["UI", "Functional"],
                priorities={"default": "High"},
                test_types=["UI Test", "Integration Test"]
            )
            logger.info("Test plan generated successfully")
            return output
        except Exception as e:
            logger.error(f"Error in planning: {str(e)}")
            raise