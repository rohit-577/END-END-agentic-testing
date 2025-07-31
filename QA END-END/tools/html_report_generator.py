import json
import os
from tools.logger import setup_logger
from typing import Dict, Any, List, TextIO

logger = setup_logger()

def generate_html_report(evaluation_results: Dict[str, List[Dict[str, Any]]], output_file: str) -> None:
    try:
        html_content: str = """
        <html>
        <head>
            <title>Test Report</title>
            <style>
                body { font-family: Arial, sans-serif; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                .passed { color: green; }
                .failed { color: red; }
            </style>
        </head>
        <body>
            <h1>Test Report</h1>
            <table>
                <tr>
                    <th>Test Type</th>
                    <th>Test ID</th>
                    <th>Status</th>
                    <th>Details</th>
                </tr>
        """
        for test_type in ["unit", "integration", "ui"]:
            for test in evaluation_results.get(test_type, []):  # type
                status: str = "Passed" if test.get("passed", False) else "Failed"
                status_class: str = "passed" if test.get("passed", False) else "failed"
                html_content += f"""
                <tr>
                    <td>{test_type}</td>
                    <td>{test.get('test_id', 'unknown')}</td>
                    <td class="{status_class}">{status}</td>
                    <td>{json.dumps(test.get('details', {}))}</td>
                </tr>
                """
        html_content += """
            </table>
        </body>
        </html>
        """
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:  # type
            f.write(html_content)
        logger.info(f"HTML report generated at {output_file}")
    except Exception as e:
        logger.error(f"Error generating HTML report: {str(e)}")
        raise

def generate_markdown_report(evaluation_results: Dict[str, List[Dict[str, Any]]], output_file: str) -> None:
    try:
        md_content: str = "# Test Report\n\n"
        md_content += "| Test Type | Test ID | Status | Details |\n"
        md_content += "|-----------|---------|--------|---------|\n"
        for test_type in ["unit", "integration", "ui"]:
            for test in evaluation_results.get(test_type, []):  # type
                status: str = "Passed" if test.get("passed", False) else "Failed"
                details: str = json.dumps(test.get("details", {})).replace("|", "\\|")
                md_content += f"| {test_type} | {test.get('test_id', 'unknown')} | {status} | {details} |\n"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:  # type
            f.write(md_content)
        logger.info(f"Markdown report generated at {output_file}")
    except Exception as e:
        logger.error(f"Error generating Markdown report: {str(e)}")
        raise