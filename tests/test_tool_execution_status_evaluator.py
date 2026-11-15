
from agent_eval.models.agent_result import AgentResult, ToolCall
from agent_eval.models.evaluation_report import EvaluationStatus
from agent_eval.models.test_case import TestCase
from agent_eval.models.trace import Trace, Span, TraceEvent
from agent_eval.evaluators.tool_execution_status_evaluator import (
    ToolExecutionStatusEvaluator,
)


def create_testcase():
    return TestCase(
        case_id="refund_001",
        name="Refund order",
        description="Test refund order",
        tags=["refund"],
        input={"message": "申请退款"},
        fixtures={},
        expected={
            "intent": "refund",
            "tool_calls": ["query_order", "refund_order"],
        },
        evaluation={
            "required_checks": ["tool_execution_status"],
        },
    )


def create_agent_result(statuses=None):
    if statuses is None:
        statuses = ["success", "success"]

    return AgentResult(
        response="退款成功",
        intent="refund",
        tool_calls=[
            ToolCall(
                name="query_order",
                arguments={"order_id": "ORDER_001"},
                status=statuses[0],
            ),
            ToolCall(
                name="refund_order",
                arguments={"order_id": "ORDER_001"},
                status=statuses[1],
            ),
        ],
        final_state={
            "order_id": "ORDER_001",
            "refund_status": "refunded",
        },
    )


def create_trace(statuses=None, end_time="2026-11-15T10:00:02+00:00"):
    if statuses is None:
        statuses = ["success", "success"]

    events = [
        TraceEvent(
            event_id=f"event_{index + 1}",
            name="tool_call",
            timestamp=f"2026-11-15T10:00:0{index + 1}+00:00",
            attributes={
                "tool_name": tool_name,
                "arguments": {"order_id": "ORDER_001"},
                "status": status,
            },
        )
        for index, (tool_name, status) in enumerate(
            zip(["query_order", "refund_order"], statuses)
        )
    ]

    span = Span(
        span_id="span_001",
        name="agent_execution",
        start_time="2026-11-15T10:00:00+00:00",
        end_time=end_time,
        status="success",
        events=events,
    )

    return Trace(
        trace_id="trace_001",
        case_id="refund_001",
        start_time="2026-11-15T10:00:00+00:00",
        end_time=end_time,
        status="completed" if end_time else "running",
        spans=[span],
    )


def test_all_tool_calls_succeed():
    evaluator = ToolExecutionStatusEvaluator()

    result = evaluator.evaluate(
        create_testcase(),
        create_agent_result(),
        create_trace(),
    )

    assert result.status == EvaluationStatus.PASS
    assert result.name == "tool_execution_status"


def test_one_tool_call_fails():
    evaluator = ToolExecutionStatusEvaluator()

    result = evaluator.evaluate(
        create_testcase(),
        create_agent_result(["success", "failed"]),
        create_trace(["success", "failed"]),
    )

    assert result.status == EvaluationStatus.FAIL
    assert result.actual == [
        {"tool_name": "query_order", "status": "success"},
        {"tool_name": "refund_order", "status": "failed"},
    ]


def test_multiple_tool_calls_partially_fail():
    evaluator = ToolExecutionStatusEvaluator()

    result = evaluator.evaluate(
        create_testcase(),
        create_agent_result(["failed", "success"]),
        create_trace(["failed", "success"]),
    )

    assert result.status == EvaluationStatus.FAIL


def test_agent_result_and_trace_status_inconsistent():
    evaluator = ToolExecutionStatusEvaluator()

    result = evaluator.evaluate(
        create_testcase(),
        create_agent_result(["success", "success"]),
        create_trace(["success", "failed"]),
    )

    assert result.status == EvaluationStatus.BLOCKED
    assert "inconsistent" in result.reason.lower()


def test_trace_is_incomplete():
    evaluator = ToolExecutionStatusEvaluator()

    result = evaluator.evaluate(
        create_testcase(),
        create_agent_result(),
        create_trace(end_time=None),
    )

    assert result.status == EvaluationStatus.BLOCKED
    assert result.reason == "Trace is incomplete."


def test_trace_tool_status_is_missing():
    evaluator = ToolExecutionStatusEvaluator()

    trace = create_trace()
    trace.spans[0].events[0].attributes.pop("status")

    agent_result = create_agent_result()

    result = evaluator.evaluate(
        create_testcase(),
        agent_result,
        trace,
    )

    assert result.status == EvaluationStatus.BLOCKED
    assert "invalid" in result.reason.lower()


def test_no_tool_calls():
    evaluator = ToolExecutionStatusEvaluator()

    agent_result = AgentResult(
        response="当前请求无需调用工具。",
        intent="general_query",
        tool_calls=[],
    )

    trace = Trace(
        trace_id="trace_002",
        case_id="general_001",
        start_time="2026-11-15T10:00:00+00:00",
        end_time="2026-11-15T10:00:01+00:00",
        status="completed",
        spans=[],
    )

    result = evaluator.evaluate(
        create_testcase(),
        agent_result,
        trace,
    )

    assert result.status == EvaluationStatus.PASS
    assert result.actual == []
