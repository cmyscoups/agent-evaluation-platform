
from agent_eval.models.agent_result import AgentResult
from agent_eval.models.evaluation_report import (
    EvaluationStatus,
    MetricResult,
)
from agent_eval.models.test_case import TestCase
from agent_eval.models.trace import Trace


class ToolCallEvaluator:

    def evaluate(
        self,
        testcase: TestCase,
        agent_result: AgentResult,
        trace: Trace,
    ) -> MetricResult:

        expected_calls = testcase.expected.get("tool_calls")

        if not isinstance(expected_calls, list):
            return MetricResult(
                name="tool_call_sequence",
                status=EvaluationStatus.BLOCKED,
                reason="Expected tool call sequence is missing or invalid.",
                expected=expected_calls,
                actual=None,
            )

        if not all(
            isinstance(name, str) and name
            for name in expected_calls
        ):
            return MetricResult(
                name="tool_call_sequence",
                status=EvaluationStatus.BLOCKED,
                reason="Expected tool call sequence contains invalid tool names.",
                expected=expected_calls,
                actual=None,
            )

        # Trace 尚未结束，无法确认完整的工具调用序列
        if trace.end_time is None:
            return MetricResult(
                name="tool_call_sequence",
                status=EvaluationStatus.BLOCKED,
                reason="Trace is incomplete.",
                expected=expected_calls,
                actual=None,
            )

        # 从 Trace 中提取实际发生的工具调用
        trace_calls = []

        for span in trace.spans:
            for event in span.events:
                if event.name != "tool_call":
                    continue

                tool_name = event.attributes.get("tool_name")

                if not isinstance(tool_name, str) or not tool_name:
                    return MetricResult(
                        name="tool_call_sequence",
                        status=EvaluationStatus.BLOCKED,
                        reason="Trace contains a tool call event with invalid tool name.",
                        expected=expected_calls,
                        actual=trace_calls,
                    )

                trace_calls.append(tool_name)

        # 检查 AgentResult 与 Trace 是否一致
        agent_calls = []

        for tool_call in agent_result.tool_calls:
            if not isinstance(tool_call.name, str) or not tool_call.name:
                return MetricResult(
                    name="tool_call_sequence",
                    status=EvaluationStatus.BLOCKED,
                    reason="AgentResult contains an invalid tool name.",
                    expected=expected_calls,
                    actual=trace_calls,
                )

            agent_calls.append(tool_call.name)

        if agent_calls != trace_calls:
            return MetricResult(
                name="tool_call_sequence",
                status=EvaluationStatus.BLOCKED,
                reason="AgentResult and Trace contain inconsistent tool call sequences.",
                expected=expected_calls,
                actual={
                    "agent_result": agent_calls,
                    "trace": trace_calls,
                },
            )

        # 严格比较预期序列与实际序列
        if expected_calls == trace_calls:
            return MetricResult(
                name="tool_call_sequence",
                status=EvaluationStatus.PASS,
                reason="Actual tool call sequence matches expected sequence.",
                expected=expected_calls,
                actual=trace_calls,
            )

        return MetricResult(
            name="tool_call_sequence",
            status=EvaluationStatus.FAIL,
            reason="Actual tool call sequence does not match expected sequence.",
            expected=expected_calls,
            actual=trace_calls,
        )
