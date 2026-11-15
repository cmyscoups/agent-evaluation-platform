
from agent_eval.models.agent_result import AgentResult
from agent_eval.models.evaluation_report import EvaluationStatus, MetricResult
from agent_eval.models.test_case import TestCase


class BusinessStateEvaluator:
    def evaluate(
        self,
        testcase: TestCase,
        agent_result: AgentResult,
    ) -> MetricResult:
        expected_state = testcase.expected.get("business_state")
        actual_state = agent_result.final_state

        if not isinstance(expected_state, dict) or not expected_state:
            return MetricResult(
                name="business_state_match",
                status=EvaluationStatus.BLOCKED,
                reason="Expected business state is missing or invalid.",
                expected=expected_state,
                actual=actual_state,
            )

        if not isinstance(actual_state, dict):
            return MetricResult(
                name="business_state_match",
                status=EvaluationStatus.BLOCKED,
                reason="Actual business state is missing or invalid.",
                expected=expected_state,
                actual=actual_state,
            )

        invalid_keys = [
            key for key in expected_state
            if not isinstance(key, str) or not key
        ]

        if invalid_keys:
            return MetricResult(
                name="business_state_match",
                status=EvaluationStatus.BLOCKED,
                reason="Expected business state contains invalid field names.",
                expected=expected_state,
                actual=actual_state,
            )

        missing_fields = [
            key for key in expected_state
            if key not in actual_state
        ]

        if missing_fields:
            return MetricResult(
                name="business_state_match",
                status=EvaluationStatus.BLOCKED,
                reason="Actual business state is missing expected fields.",
                expected=expected_state,
                actual=actual_state,
            )

        mismatched_fields = {
            key: {
                "expected": expected_state[key],
                "actual": actual_state[key],
            }
            for key in expected_state
            if expected_state[key] != actual_state[key]
        }

        if mismatched_fields:
            return MetricResult(
                name="business_state_match",
                status=EvaluationStatus.FAIL,
                reason="Actual business state does not match expected state.",
                expected=expected_state,
                actual=actual_state,
            )

        return MetricResult(
            name="business_state_match",
            status=EvaluationStatus.PASS,
            reason="Actual business state matches expected state.",
            expected=expected_state,
            actual=actual_state,
        )
