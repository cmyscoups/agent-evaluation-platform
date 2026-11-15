
from agent_eval.models.agent_result import AgentResult
from agent_eval.models.evaluation_report import EvaluationStatus, MetricResult
from agent_eval.models.test_case import TestCase
from agent_eval.models.trace import Trace


class ToolExecutionStatusEvaluator:
    def evaluate(
        self,
        testcase: TestCase,
        agent_result: AgentResult,
        trace: Trace,
    ) -> MetricResult:
        if trace.end_time is None:
            return MetricResult(
                name="tool_execution_status",
                status=EvaluationStatus.BLOCKED,
                reason="Trace is incomplete.",
                expected="All tool calls succeed.",
                actual=None,
            )

        trace_calls = []

        for span in trace.spans:
            for event in span.events:
                if event.name != "tool_call":
                    continue

                tool_name = event.attributes.get("tool_name")
                status = event.attributes.get("status")

                if not isinstance(tool_name, str) or not tool_name:
                    return MetricResult(
                        name="tool_execution_status",
                        status=EvaluationStatus.BLOCKED,
                        reason="Trace contains a tool call event with invalid tool name.",
                        expected="All tool calls succeed.",
                        actual=trace_calls,
                    )

                if status not in ("success", "failed"):
                    return MetricResult(
                        name="tool_execution_status",
                        status=EvaluationStatus.BLOCKED,
                        reason="Trace contains a missing or invalid tool execution status.",
                        expected="All tool calls succeed.",
                        actual=trace_calls,
                    )

                trace_calls.append({
                    "tool_name": tool_name,
                    "status": status,
                })

        agent_calls = []

        for tool_call in agent_result.tool_calls:
            if not isinstance(tool_call.name, str) or not tool_call.name:
                return MetricResult(
                    name="tool_execution_status",
                    status=EvaluationStatus.BLOCKED,
                    reason="AgentResult contains an invalid tool name.",
                    expected="All tool calls succeed.",
                    actual=trace_calls,
                )

            if tool_call.status not in ("success", "failed"):
                return MetricResult(
                    name="tool_execution_status",
                    status=EvaluationStatus.BLOCKED,
                    reason="AgentResult contains a missing or invalid tool execution status.",
                    expected="All tool calls succeed.",
                    actual=trace_calls,
                )

            agent_calls.append({
                "tool_name": tool_call.name,
                "status": tool_call.status,
            })

        if agent_calls != trace_calls:
            return MetricResult(
                name="tool_execution_status",
                status=EvaluationStatus.BLOCKED,
                reason="AgentResult and Trace contain inconsistent tool execution records.",
                expected="All tool calls succeed.",
                actual={
                    "agent_result": agent_calls,
                    "trace": trace_calls,
                },
            )

        failed_calls = [
            call for call in trace_calls
            if call["status"] == "failed"
        ]

        if failed_calls:
            return MetricResult(
                name="tool_execution_status",
                status=EvaluationStatus.FAIL,
                reason="One or more tool calls failed.",
                expected="All tool calls succeed.",
                actual=trace_calls,
            )

        return MetricResult(
            name="tool_execution_status",
            status=EvaluationStatus.PASS,
            reason="All tool calls succeeded.",
            expected="All tool calls succeed.",
            actual=trace_calls,
        )
