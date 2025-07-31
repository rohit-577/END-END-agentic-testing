from tools.logger import setup_logger
import subprocess
import json
import os
from typing import Dict, Any, List, TextIO

logger = setup_logger()

class CoverageAnalyzer:
    def analyze_coverage(self, test_files: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
        try:
            coverage_data: Dict[str, Dict[str, Any]] = {}
            cov_report_file: str = os.path.join("results", "test_logs", "coverage.json")
            os.makedirs(os.path.dirname(cov_report_file), exist_ok=True)

            for test_type, test_file in test_files.items():  # type
                logger.debug(f"Running coverage for {test_type}: {test_file}")
                if not os.path.exists(test_file):
                    logger.warning(f"Test file {test_file} does not exist, skipping")
                    continue
                cmd = ["pytest", test_file, "--cov", "--cov-report=json:tmp_cov.json"]
                subprocess.run(cmd, capture_output=True, text=True)
                if os.path.exists("tmp_cov.json"):
                    with open("tmp_cov.json", "r", encoding="utf-8") as f:  # type
                        coverage_data[test_type] = json.load(f)
                    os.remove("tmp_cov.json")
                else:
                    logger.warning(f"No coverage data generated for {test_type}")

            with open(cov_report_file, "w", encoding="utf-8") as f:  # type
                json.dump(coverage_data, f, indent=2)
            logger.info("Coverage analysis completed: %s", coverage_data)
            return coverage_data
        except Exception as e:
            logger.error(f"Error analyzing coverage: {str(e)}")
            raise