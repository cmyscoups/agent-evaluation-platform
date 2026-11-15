
from agent_eval.models.agent_result import AgentResult
from agent_eval.models.evaluation_report import EvaluationStatus, MetricResult
from agent_eval.models.test_case import TestCase


class ResponseEvaluator:
    def evaluate(
        self,
        testcase: TestCase,
        agent_result: AgentResult,
    ) -> MetricResult:
        expected_response = testcase.expected.get("response")

        if not isinstance(expected_response, dict):
            return MetricResult(
                name="response_check",
                status=EvaluationStatus.BLOCKED,
                reason="Expected response configuration is missing or invalid.",
                expected=expected_response,
                actual=agent_result.response,
            )

        must_include = expected_response.get("must_include")

        if (
            not isinstance(must_include, list)
            or not must_include
            or not all(
                isinstance(item, str) and item.strip()
                for item in must_include
            )
        ):
            return MetricResult(
                name="response_check",
                status=EvaluationStatus.BLOCKED,
                reason="Expected must_include configuration is missing or invalid.",
                expected=must_include,
                actual=agent_result.response,
            )

        actual_response = agent_result.response

        if not isinstance(actual_response, str):
            return MetricResult(
                name="response_check",
                status=EvaluationStatus.BLOCKED,
                reason="Actual response is missing or invalid.",
                expected=must_include,
                actual=actual_response,
            )

        missing_items = [
            item for item in must_include
            if item not in actual_response
        ]

        if missing_items:
            return MetricResult(
                name="response_check",
                status=EvaluationStatus.FAIL,
                reason="Actual response does not contain all required content.",
                expected=must_include,
                actual={
                    "response": actual_response,
                    "missing_items": missing_items,
                },
            )

        return MetricResult(
            name="response_check",
            status=EvaluationStatus.PASS,
            reason="Actual response contains all required content.",
            expected=must_include,
            actual=actual_response,
        )
