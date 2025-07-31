from langgraph.graph import StateGraph, END
from agents.planner import Planner
from agents.test_writer import TestWriter
from agents.ui_agent import UIAgent
from agents.runner import TestRunner
from agents.evaluator import Evaluator
from agents.reporter import Reporter
from tools.coverage_analyzer import CoverageAnalyzer
from tools.logger import setup_logger
import asyncio
from typing import Dict, Any, List, TypedDict, Optional, Protocol, AsyncIterator

logger = setup_logger()

# Define state schema as a TypedDict to structure the state
class AgentState(TypedDict):
    planner_output: Optional[Dict[str, Any]]  # Contains the PlannerOutput object
    test_files: Optional[Dict[str, str]]
    ui_output: Optional[Dict[str, Any]]
    test_results: Optional[Dict[str, List[Dict[str, Any]]]]
    evaluation_results: Optional[Dict[str, Any]]
    coverage_data: Optional[Dict[str, Dict[str, Any]]]

# Define protocol for compiled graph to type astream
class CompiledGraphProtocol(Protocol):
    async def astream(self, input: AgentState) -> AsyncIterator[Dict[str, Any]]:
        ...

class CrewMaster:
    def __init__(self, ui_config: Dict[str, Any], pr_diff: Dict[str, Any]) -> None:
        self.ui_config: Dict[str, Any] = ui_config
        self.pr_diff: Dict[str, Any] = pr_diff
        self.graph: CompiledGraphProtocol = self._build_graph()

    def _build_graph(self) -> CompiledGraphProtocol:
        graph = StateGraph(AgentState)
        graph.add_node("plan", self.plan_node)
        graph.add_node("write_tests", self.write_tests_node)
        graph.add_node("ui_tests", self.ui_tests_node)
        graph.add_node("run_tests", self.run_tests_node)
        graph.add_node("evaluate", self.evaluate_node)
        graph.add_node("coverage", self.coverage_node)
        graph.add_node("report", self.report_node)
        graph.add_edge("plan", "write_tests")
        graph.add_edge("write_tests", "ui_tests")
        graph.add_edge("ui_tests", "run_tests")
        graph.add_edge("run_tests", "evaluate")
        graph.add_edge("evaluate", "coverage")
        graph.add_edge("coverage", "report")
        graph.add_edge("report", END)
        graph.set_entry_point("plan")
        return graph.compile()

    async def plan_node(self, state: AgentState) -> Dict[str, Any]:
        try:
            planner = Planner(self.ui_config, self.pr_diff)
            planner_output: Dict[str, Any] = {"planner_output": planner.plan().dict()}  # Convert to dict
            logger.debug("Plan node output: %s", planner_output)
            return planner_output
        except Exception as e:
            logger.error(f"Error in plan node: {str(e)}")
            raise

    async def write_tests_node(self, state: AgentState) -> Dict[str, Any]:
        try:
            logger.debug("Current state in write_tests_node: %s", state)
            planner_output: Optional[Dict[str, Any]] = state.get("planner_output")
            if not planner_output or "planner_output" not in planner_output:
                logger.error("Planner output not found in state: %s", state)
                raise ValueError("Planner output not found in state")
            planner_obj: Dict[str, Any] = planner_output["planner_output"]
            test_writer = TestWriter()
            test_files: Dict[str, str] = test_writer.write_tests(planner_obj, self.ui_config)
            logger.info("Write tests node completed: %s", test_files)
            return {"test_files": test_files}
        except Exception as e:
            logger.error(f"Error in write_tests node: {str(e)}")
            raise

    async def ui_tests_node(self, state: AgentState) -> Dict[str, Any]:
        try:
            ui_agent = UIAgent(self.ui_config)
            ui_output: Dict[str, Any] = (await ui_agent.execute_ui_flow()).dict()
            logger.info("UI tests node completed: %s", ui_output)
            return {"ui_output": ui_output}
        except Exception as e:
            logger.error(f"Error in UI tests node: {str(e)}")
            raise

    async def run_tests_node(self, state: AgentState) -> Dict[str, Any]:
        try:
            test_files: Optional[Dict[str, str]] = state.get("test_files")
            if not test_files:
                logger.error("Test files not found in state: %s", state)
                raise ValueError("Test files not found in state")
            test_runner = TestRunner()
            test_results: Dict[str, List[Dict[str, Any]]] = test_runner.run_tests(test_files)
            logger.info("Run tests node completed: %s", test_results)
            return {"test_results": test_results}
        except Exception as e:
            logger.error(f"Error in run tests node: {str(e)}")
            raise

    async def evaluate_node(self, state: AgentState) -> Dict[str, Any]:
        try:
            test_results: Optional[Dict[str, List[Dict[str, Any]]]] = state.get("test_results")
            if not test_results:
                logger.error("Test results not found in state: %s", state)
                raise ValueError("Test results not found in state")
            evaluator = Evaluator()
            evaluation_results: Dict[str, Any] = evaluator.evaluate(test_results)
            logger.info("Evaluate node completed: %s", evaluation_results)
            return {"evaluation_results": evaluation_results}
        except Exception as e:
            logger.error(f"Error in evaluate node: {str(e)}")
            raise

    async def coverage_node(self, state: AgentState) -> Dict[str, Any]:
        try:
            test_files: Optional[Dict[str, str]] = state.get("test_files")
            if not test_files:
                logger.error("Test files not found in state: %s", state)
                raise ValueError("Test files not found in state")
            coverage_analyzer = CoverageAnalyzer()
            coverage_data: Dict[str, Dict[str, Any]] = coverage_analyzer.analyze_coverage(test_files)
            logger.info("Coverage node completed: %s", coverage_data)
            return {"coverage_data": coverage_data}
        except Exception as e:
            logger.error(f"Error in coverage node: {str(e)}")
            raise

    async def report_node(self, state: AgentState) -> Dict[str, Any]:
        try:
            evaluation_results: Optional[Dict[str, Any]] = state.get("evaluation_results")
            if not evaluation_results:
                logger.error("Evaluation results not found in state: %s", state)
                raise ValueError("Evaluation results not found in state")
            reporter = Reporter()
            reporter.generate_report(evaluation_results)
            logger.info("Report node completed")
            return {}
        except Exception as e:
            logger.error(f"Error in report node: {str(e)}")
            raise

    async def run(self) -> None:
        try:
            state: AgentState = {
                "planner_output": None,
                "test_files": None,
                "ui_output": None,
                "test_results": None,
                "evaluation_results": None,
                "coverage_data": None
            }
            logger.debug("Initial state: %s", state)
            async for event in self.graph.astream(state):  # type
                logger.debug("Received event: %s", event)
                if isinstance(event, dict):
                    logger.debug("Updating state with event: %s", event)
                    state.update(event)
            logger.debug("Final state: %s", state)
            logger.info("CrewMaster execution completed")
        except Exception as e:
            logger.error(f"Error in CrewMaster run: {str(e)}")
            raise