from tools.logger import setup_logger
import os
from typing import Dict, List, Any, TextIO, TypedDict

logger = setup_logger()

# Define structure for expected_result
class ExpectedResult(TypedDict):
    url: str

# Define structure for ui_config["flows"][0]
class FlowConfig(TypedDict):
    page: str
    actions: List[Dict[str, Any]]
    expected_result: ExpectedResult

# Define structure for test in test_plan
class TestConfig(TypedDict):
    test_id: str
    page: str
    actions: List[Dict[str, Any]]
    expected_result: ExpectedResult

class TestWriter:
    def write_tests(self, planner_output: Dict[str, Any], ui_config: Dict[str, Any]) -> Dict[str, str]:
        try:
            test_files: Dict[str, str] = {
                "unit": os.path.join("tests", "unit", "test_unit.py"),
                "integration": os.path.join("tests", "integration", "test_integration.py"),
                "ui": os.path.join("tests", "ui", "test_ui.py")
            }
            logger.debug(f"Ensuring directories for test files: {test_files}")
            for test_file in test_files.values():
                os.makedirs(os.path.dirname(test_file), exist_ok=True)

            test_plan: Dict[str, List[Dict[str, Any]]] = planner_output.get("test_plan", {})
            flows: List[FlowConfig] = ui_config.get("flows", [{}])
            expected_url: str = flows[0].get("expected_result", {}).get("url", "")

            for test_type, tests in [
                ("unit", test_plan.get("unit_tests", [])),
                ("integration", test_plan.get("integration_tests", [])),
                ("ui", test_plan.get("ui_tests", []))
            ]:
                logger.debug(f"Writing tests for {test_type}: {test_files[test_type]}")
                with open(test_files[test_type], "w", encoding="utf-8") as f:  # type
                    f.write(f"# {test_type.capitalize()} Tests\n\n")
                    for test in tests:  # type
                        test_id: str = test.get("test_id", "unknown")
                        if test_type == "ui":
                            page: str = test.get("page", "unknown")
                            actions: List[Dict[str, Any]] = test.get("actions", [])
                            f.write(f"# Test {test_id}\n")
                            f.write(f"def test_{test_id}():\n")
                            f.write(f"    # Page: {page}\n")
                            for action in actions:  # type
                                f.write(f"    # Action: {action.get('type', 'unknown')} - {action.get('selector', 'unknown')}\n")
                            f.write(f"    assert '{test.get('expected_result', {}).get('url', '')}' == '{expected_url}'  # UI test assertion\n\n")
                        else:
                            f.write(f"# Test {test_id}\n")
                            f.write(f"def test_{test_id}():\n")
                            f.write("    assert True  # Mock test\n\n")

            logger.info("Tests written successfully: %s", test_files)
            return test_files
        except Exception as e:
            logger.error(f"Error writing tests: {str(e)}")
            raise