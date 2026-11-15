
import pytest

from agent_eval.evaluators.tool_call_evaluator import ToolCallEvaluator
from agent_eval.models.agent_result import AgentResult, ToolCall
from agent_eval.models.evaluation_report import EvaluationStatus
from agent_eval.models.test_case import TestCase
from agent_eval.models.trace import Trace, Span, TraceEvent


@pytest.fixture
def evaluator():
    return ToolCallEvaluator()


def create_testcase(expected_calls):
    return TestCase(
        case_id="case_001",
        name="test tool calls",
        description="test tool call sequence",
        tags=[],
        input={},
        fixtures={},
        expected={"tool_calls": expected_calls},
        evaluation={},
    )


def create_agent_result(tool_names):
    return AgentResult(
        response="test response",
        intent="refund",
        tool_calls=[
            ToolCall(name=name, arguments={})
            for name in tool_names
        ],
    )


def create_trace(tool_names, completed=True):
    events = [
        TraceEvent(
            event_id=f"event_{index}",
            name="tool_call",
            timestamp=f"2026-11-14T10:00:0{index}+00:00",
            attributes={
                "tool_name": name,
                "arguments": {},
                "status": "success",
            },
        )
        for index, name in enumerate(tool_names)
    ]

    span = Span(
        span_id="span_001",
        name="agent_execution",
        start_time="2026-11-14T10:00:00+00:00",
        end_time="2026-11-14T10:00:10+00:00",
        status="success",
        events=events,
    )

    return Trace(
        trace_id="trace_001",
        case_id="case_001",
        start_time="2026-11-14T10:00:00+00:00",
        end_time=(
            "2026-11-14T10:00:10+00:00"
            if completed else None
        ),
        status="completed" if completed else "running",
        spans=[span],
    )


def test_correct_sequence_returns_pass(evaluator):
    result = evaluator.evaluate(
        create_testcase(["query_order", "refund_order"]),
        create_agent_result(["query_order", "refund_order"]),
        create_trace(["query_order", "refund_order"]),
    )

    assert result.status == EvaluationStatus.PASS


def test_wrong_sequence_returns_fail(evaluator):
    result = evaluator.evaluate(
        create_testcase(["query_order", "refund_order"]),
        create_agent_result(["refund_order", "query_order"]),
        create_trace(["refund_order", "query_order"]),
    )

    assert result.status == EvaluationStatus.FAIL


def test_missing_tool_call_returns_fail(evaluator):
    result = evaluator.evaluate(
        create_testcase(["query_order", "refund_order"]),
        create_agent_result(["query_order"]),
        create_trace(["query_order"]),
    )

    assert result.status == EvaluationStatus.FAIL


def test_extra_tool_call_returns_fail(evaluator):
    result = evaluator.evaluate(
        create_testcase(["query_order", "refund_order"]),
        create_agent_result(
            ["query_order", "refund_order", "query_order"]
        ),
        create_trace(
            ["query_order", "refund_order", "query_order"]
        ),
    )

    assert result.status == EvaluationStatus.FAIL


def test_inconsistent_evidence_returns_blocked(evaluator):
    result = evaluator.evaluate(
        create_testcase(["query_order", "refund_order"]),
        create_agent_result(["query_order", "refund_order"]),
        create_trace(["query_order"]),
    )

    assert result.status == EvaluationStatus.BLOCKED


def test_incomplete_trace_returns_blocked(evaluator):
    result = evaluator.evaluate(
        create_testcase(["query_order", "refund_order"]),
        create_agent_result(["query_order"]),
        create_trace(["query_order"], completed=False),
    )

    assert result.status == EvaluationStatus.BLOCKED
