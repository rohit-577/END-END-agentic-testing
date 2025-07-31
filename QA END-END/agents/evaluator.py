from tools.logger import setup_logger
import json
import os
from typing import Dict, Any, List, TextIO, TypedDict

logger = setup_logger()

# Define structure for evaluation_summary
class EvaluationSummary(TypedDict):
    total_tests: int
    passed: int
    failed: int
    ui_tests: List[Dict[str, Any]]

class Evaluator:
    def evaluate(self, test_results: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        try:
            evaluation_summary: EvaluationSummary = {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "ui_tests": []
            }
            results_file: str = os.path.join("results", "test_logs", "results.json")
            if os.path.exists(results_file):
                with open(results_file, "r", encoding="utf-8") as f:  # type
                    results: Dict[str, List[Dict[str, Any]]] = json.load(f)
            else:
                results = test_results

            for test_type in ["unit", "integration", "ui"]:
                for test in results.get(test_type, []):  # type
                    evaluation_summary["total_tests"] += 1
                    if test.get("passed", False):
                        evaluation_summary["passed"] += 1
                    else:
                        evaluation_summary["failed"] += 1
                    if test_type == "ui":
                        evaluation_summary["ui_tests"].append({
                            "test_id": test.get("test_id", "unknown"),
                            "passed": test.get("passed", False),
                            "details": test.get("details", {})
                        })

            os.makedirs("results", exist_ok=True)
            with open("results/evaluation_summary.json", "w", encoding="utf-8") as f:  # type
                json.dump(evaluation_summary, f, indent=2)

            logger.info("Evaluation completed successfully: %s", evaluation_summary)
            return evaluation_summary
        except Exception as e:
            logger.error(f"Error in evaluation: {str(e)}")
            raise