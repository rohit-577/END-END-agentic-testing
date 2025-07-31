import subprocess
import json
import os
from tools.logger import setup_logger
from typing import Dict, Any, List, TextIO, TypedDict, Optional

logger = setup_logger()

# Define structure of a single test result from pytest JSON report
class TestResult(TypedDict):
    nodeid: Optional[str]
    outcome: Optional[str]
    call: Optional[Dict[str, Any]]

class TestRunner:
    def run_tests(self, test_files: Dict[str, str]) -> Dict[str, List[Dict[str, Any]]]:
        try:
            results: Dict[str, List[Dict[str, Any]]] = {"unit": [], "integration": [], "ui": []}
            os.makedirs("results/test_logs", exist_ok=True)
            results_file: str = os.path.join("results", "test_logs", "results.json")

            for test_type, test_file in test_files.items():  # type
                logger.debug(f"Running tests for {test_type}: {test_file}")
                if not os.path.exists(test_file):
                    logger.warning(f"Test file {test_file} does not exist, skipping")
                    continue
                cmd = ["pytest", test_file, "--json-report", "--json-report-file=tmp.json"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if os.path.exists("tmp.json"):
                    with open("tmp.json", "r", encoding="utf-8") as f:  # type
                        test_data: Dict[str, Any] = json.load(f)
                    tests: List[TestResult] = test_data.get("tests", [])  # Explicitly type as List[TestResult]
                    results[test_type] = [
                        {
                            "test_id": test.get("nodeid", "unknown"),
                            "passed": test.get("outcome", "") == "passed",
                            "details": test.get("call", {})
                        } for test in tests  # type: TestResult
                    ]
                    os.remove("tmp.json")
                else:
                    logger.warning(f"No test results generated for {test_type}")

            with open(results_file, "w", encoding="utf-8") as f:  # type
                json.dump(results, f, indent=2)
            logger.info("Tests executed successfully: %s", results)
            return results
        except Exception as e:
            logger.error(f"Error running tests: {str(e)}")
            raise