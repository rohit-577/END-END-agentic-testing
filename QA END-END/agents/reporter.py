from tools.logger import setup_logger
from tools.html_report_generator import generate_html_report, generate_markdown_report
import os
from typing import Dict, Any, List

logger = setup_logger()

class Reporter:
    def generate_report(self, evaluation_results: Dict[str, Any]) -> None:
        try:
            os.makedirs("results", exist_ok=True)
            html_report_path: str = os.path.join("results", "final_report.html")
            md_report_path: str = os.path.join("results", "report_summary.md")

            # Convert evaluation_results to expected format if needed
            formatted_results: Dict[str, List[Dict[str, Any]]] = {
                "unit": [],
                "integration": [],
                "ui": evaluation_results.get("ui_tests", [])
            }

            generate_html_report(formatted_results, html_report_path)
            generate_markdown_report(formatted_results, md_report_path)
            logger.info(f"Reports generated at {html_report_path} and {md_report_path}")
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            raise