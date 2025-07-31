# FileName: MultipleFiles/tasks.py
# FileContents:
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class TestCase(BaseModel):
    """Schema for individual test cases."""
    id: str
    description: str
    steps: List[str]
    expected_result: str
    actual_result: Optional[str] = None
    passed: Optional[bool] = None
    error: Optional[str] = None # Added to capture error messages for failed tests

class AssertionResult(BaseModel):
    """Schema for assertion results."""
    description: str
    passed: bool
    details: Optional[str] = None

class UITestFlow(BaseModel):
    """Schema for UI test flows executed by UIAgent."""
    name: str
    steps: List[str]
    success_criteria: str
    screenshots: Optional[List[str]] = []
    metadata: Dict[str, Any] = {} # Changed to Any to allow for status, error, etc.

class UIAgentInput(BaseModel):
    """Input schema for UIAgent, containing UI configuration."""
    ui_config: Dict[str, Any]

class UIAgentOutput(BaseModel):
    """Output schema for UIAgent, referencing test and result files."""
    ui_test_flows: List[UITestFlow]
    screenshot_diffs: List[Dict[str, str]]
    login_status: str
    generated_test_file: str  # Path to tests/ui
    results_file: str  # Path to results/test_logs (for UI specific results)
    screenshots_file: str  # Path to results/screenshots (for screenshot metadata)

class PlannerInput(BaseModel):
    """Input schema for Planner, containing UI config and PR details."""
    ui_config: Dict[str, Any]
    diff: Optional[str] = None # Raw diff text, might be deprecated by changed_files
    pr_url: Optional[str] = None
    repo_url: Optional[str] = None
    base_branch: Optional[str] = None
    head_branch: Optional[str] = None
    changed_files: Optional[List[str]] = None # List of file paths changed in PR

class PlannerOutput(BaseModel):
    """Output schema for Planner, defining test goals and priorities."""
    test_goals: List[str]
    test_categories: List[str] # e.g., ["unit", "integration", "ui"]
    priorities: Dict[str, str] # e.g., {"ui": "high"}
    test_types: List[str] # e.g., ["unit", "integration", "ui"]

class TestWriterInput(BaseModel):
    """Input schema for TestWriter, containing test plan and UI config."""
    test_plan: Dict[str, Any]
    ui_config: Dict[str, Any]

class TestWriterOutput(BaseModel):
    """Output schema for TestWriter, mapping tests to file paths."""
    generated_tests: Dict[str, str]  # Maps to tests/unit, tests/integration, tests/ui
    notes: Optional[str] = None

class EvaluatorInput(BaseModel):
    """Input schema for Evaluator, containing execution results and UI config."""
    # execution_results now contains lists of dictionaries (TestCase.dict())
    execution_results: Dict[str, List[Dict[str, Any]]]
    ui_config: Dict[str, Any]

class EvaluatorOutput(BaseModel):
    """Output schema for Evaluator, containing evaluation summary."""
    evaluation_summary: Dict[str, Dict[str, int]]
    rationale: Optional[str] = None
    results_file: str  # Path to results/test_logs/evaluation_summary.json

class RunnerInput(BaseModel):
    """Input schema for Runner, containing generated tests and UI config."""
    generated_tests: Dict[str, str] # Paths to generated test files
    ui_config: Dict[str, Any]

class RunnerOutput(BaseModel):
    """Output schema for Runner, containing execution results and logs."""
    # execution_results now contains lists of dictionaries (TestCase.dict())
    execution_results: Dict[str, List[Dict[str, Any]]]
    logs: Optional[List[str]] = None
    results_file: str  # Path to the directory containing test results (e.g., results/test_logs)

class ReporterInput(BaseModel):
    """Input schema for Reporter, containing results and summary."""
    execution_results: Dict[str, Any] # Can be Dict[str, List[Dict[str, Any]]] or just summary
    evaluation_summary: Dict[str, Any]
    ui_config: Dict[str, Any] # For context if needed in reports

class ReporterOutput(BaseModel):
    """Output schema for Reporter, containing report paths and summary."""
    reports_file: str  # Path to results/reports/report_summary.json
    html_report_file: Optional[str] = None # Path to the generated HTML report
    markdown_report_file: Optional[str] = None # Path to the generated Markdown report
    summary: str
    total_tests: Optional[int] = 0
    passed: Optional[int] = 0
    failed: Optional[int] = 0

