
from agent_eval.models.agent_result import AgentResult
from agent_eval.models.evaluation_report import (
    EvaluationStatus,
    MetricResult,
)
from agent_eval.models.test_case import TestCase


class IntentEvaluator:

    def evaluate(
        self,
        testcase: TestCase,
        agent_result: AgentResult,
    ) -> MetricResult:
        expected_intent = testcase.expected.get("intent")
        actual_intent = agent_result.intent

        if expected_intent is None:
            return MetricResult(
                name="intent_match",
                status=EvaluationStatus.BLOCKED,
                reason="Expected intent is missing.",
                expected=None,
                actual=actual_intent,
            )

        if actual_intent is None:
            return MetricResult(
                name="intent_match",
                status=EvaluationStatus.BLOCKED,
                reason="Actual intent is missing.",
                expected=expected_intent,
                actual=None,
            )

        if expected_intent == actual_intent:
            return MetricResult(
                name="intent_match",
                status=EvaluationStatus.PASS,
                reason="Actual intent matches expected intent.",
                expected=expected_intent,
                actual=actual_intent,
            )

        return MetricResult(
            name="intent_match",
            status=EvaluationStatus.FAIL,
            reason="Actual intent does not match expected intent.",
            expected=expected_intent,
            actual=actual_intent,
        )
