from tools.logger import setup_logger
import json
from typing import Dict, Any

logger = setup_logger()

class CITrigger:
    def trigger_ci_pipeline(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Extract test results with defaults
            total_tests = test_results.get("total_tests", 0)
            passed = test_results.get("passed", 0)
            failed = test_results.get("failed", 0)
            
            if total_tests > 0 and failed == 0:
                logger.info("All tests passed, triggering CI pipeline")
                return {"status": "success", "pipeline_id": "mock_pipeline"}
            else:
                logger.warning(f"Tests failed or incomplete (Passed: {passed}, Failed: {failed}). Skipping CI trigger.")
                return {"status": "skipped", "reason": f"Failed tests: {failed}"}
        except Exception as e:
            logger.error(f"Error triggering CI pipeline: {str(e)}")
            raise