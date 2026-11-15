
from unittest.mock import Mock

import pytest

from agent_eval.runner import EvaluationRunner
from agent_eval.collectors.trace_collector import TraceCollector
from agent_eval.models.test_case import TestCase


def make_testcase():
    return TestCase(
        case_id="case_001",
        name="Test case",
        description="Test runner",
        tags=[],
        input={},
        fixtures={},
        expected={},
        evaluation={"required_checks": ["intent_match"]},
    )


def test_runner_returns_evaluation_report():
    testcase = make_testcase()

    collector = TraceCollector()
    agent_adapter = Mock()
    evaluator = Mock()

    agent_result = object()
    expected_report = object()

    agent_adapter.run.return_value = agent_result
    evaluator.evaluate.return_value = expected_report

    runner = EvaluationRunner(
        agent_adapter=agent_adapter,
        evaluator=evaluator,
        collector=collector,
    )

    report = runner.run(testcase)

    trace = collector.get_trace()

    assert report is expected_report
    assert trace.status == "completed"
    assert trace.end_time is not None

    agent_adapter.run.assert_called_once_with(testcase)
    evaluator.evaluate.assert_called_once_with(
        testcase,
        agent_result,
        trace,
    )


def test_runner_marks_trace_failed_when_agent_raises():
    testcase = make_testcase()

    collector = TraceCollector()
    agent_adapter = Mock()
    evaluator = Mock()

    agent_adapter.run.side_effect = RuntimeError("Agent execution failed")

    runner = EvaluationRunner(
        agent_adapter=agent_adapter,
        evaluator=evaluator,
        collector=collector,
    )

    with pytest.raises(
        RuntimeError,
        match="Agent execution failed",
    ):
        runner.run(testcase)

    trace = collector.get_trace()

    assert trace.status == "failed"
    assert trace.end_time is not None

    evaluator.evaluate.assert_not_called()


def test_runner_ends_active_span_when_agent_raises():
    testcase = make_testcase()

    collector = TraceCollector()
    agent_adapter = Mock()
    evaluator = Mock()

    def execute_with_error(testcase):
        collector.start_span("query_order")
        raise RuntimeError("Tool execution failed")

    agent_adapter.run.side_effect = execute_with_error

    runner = EvaluationRunner(
        agent_adapter=agent_adapter,
        evaluator=evaluator,
        collector=collector,
    )

    with pytest.raises(RuntimeError, match="Tool execution failed"):
        runner.run(testcase)

    trace = collector.get_trace()

    assert trace.status == "failed"
    assert len(trace.spans) == 1
    assert trace.spans[0].status == "failed"
    assert trace.spans[0].end_time is not None

    evaluator.evaluate.assert_not_called()


def test_runner_passes_same_trace_to_evaluator():
    testcase = make_testcase()

    collector = TraceCollector()
    agent_adapter = Mock()
    evaluator = Mock()

    agent_adapter.run.return_value = object()

    runner = EvaluationRunner(
        agent_adapter=agent_adapter,
        evaluator=evaluator,
        collector=collector,
    )

    runner.run(testcase)

    trace = collector.get_trace()
    actual_trace = evaluator.evaluate.call_args.args[2]

    assert actual_trace is trace
