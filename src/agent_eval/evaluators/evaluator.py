
import logging

from agent_eval.models.agent_result import AgentResult
from agent_eval.models.evaluation_report import (
    EvaluationReport,
    EvaluationStatus,
    MetricResult,
)
from agent_eval.models.test_case import TestCase
from agent_eval.models.trace import Trace

from agent_eval.evaluators.intent_evaluator import IntentEvaluator
from agent_eval.evaluators.tool_call_evaluator import ToolCallEvaluator
from agent_eval.evaluators.tool_execution_status_evaluator import (
    ToolExecutionStatusEvaluator,
)
from agent_eval.evaluators.business_state_evaluator import (
    BusinessStateEvaluator,
)
from agent_eval.evaluators.response_evaluator import ResponseEvaluator


logger = logging.getLogger(__name__)


class Evaluator:
    def __init__(self):
        self.intent_evaluator = IntentEvaluator()
        self.tool_call_evaluator = ToolCallEvaluator()
        self.tool_execution_status_evaluator = (
            ToolExecutionStatusEvaluator()
        )
        self.business_state_evaluator = BusinessStateEvaluator()
        self.response_evaluator = ResponseEvaluator()

        self.evaluator_registry = {
            "intent_match": self.intent_evaluator.evaluate,
            "tool_call_sequence": self.tool_call_evaluator.evaluate,
            "tool_execution_status": (
                self.tool_execution_status_evaluator.evaluate
            ),
            "business_state_match": (
                self.business_state_evaluator.evaluate
            ),
            "response_check": self.response_evaluator.evaluate,
        }

    def evaluate(
        self,
        testcase: TestCase,
        agent_result: AgentResult,
        trace: Trace,
    ) -> EvaluationReport:
        evaluation_config = testcase.evaluation

        if not isinstance(evaluation_config, dict):
            return EvaluationReport(
                testcase_id=testcase.case_id,
                results=(
                    MetricResult(
                        name="required_checks",
                        status=EvaluationStatus.BLOCKED,
                        reason="Evaluation configuration is missing or invalid.",
                        expected="A valid required_checks list.",
                        actual=evaluation_config,
                    ),
                ),
            )

        required_checks = evaluation_config.get("required_checks")

        if (
            not isinstance(required_checks, list)
            or not required_checks
            or not all(
                isinstance(name, str) and name
                for name in required_checks
            )
        ):
            return EvaluationReport(
                testcase_id=testcase.case_id,
                results=(
                    MetricResult(
                        name="required_checks",
                        status=EvaluationStatus.BLOCKED,
                        reason="required_checks is missing, empty, or invalid.",
                        expected="A non-empty list of metric names.",
                        actual=required_checks,
                    ),
                ),
            )

        results = []

        for metric_name in required_checks:
            evaluator = self.evaluator_registry.get(metric_name)

            if evaluator is None:
                logger.warning(
                    "Unknown evaluation metric: %s",
                    metric_name,
                )

                results.append(
                    MetricResult(
                        name=metric_name,
                        status=EvaluationStatus.BLOCKED,
                        reason=f"Unknown evaluation metric: {metric_name}.",
                        expected="A registered evaluation metric.",
                        actual=None,
                    )
                )
                continue

            if metric_name in (
                "intent_match",
                "business_state_match",
                "response_check",
            ):
                result = evaluator(testcase, agent_result)
            else:
                result = evaluator(testcase, agent_result, trace)

            results.append(result)

        return EvaluationReport(
            testcase_id=testcase.case_id,
            results=tuple(results),
        )
