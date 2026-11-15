
from agent_eval.models.test_case import TestCase
import pytest

import agent_eval.evaluators.evaluator as evaluator_module
from agent_eval.evaluators.evaluator import Evaluator
from agent_eval.models.evaluation_report import (
    EvaluationStatus,
    MetricResult,
)


def make_testcase(required_checks=None):
    return TestCase(
        case_id="case_001",
        name="Test case",
        description="Test case for evaluator",
        tags=[],
        input={},
        fixtures={},
        expected={},
        evaluation={"required_checks": required_checks},
    )

def make_metric_result(name, status=EvaluationStatus.PASS):
    return MetricResult(
        name=name,
        status=status,
        reason=f"{name} evaluated",
    )


def make_stub_class(metric_name, calls, status=EvaluationStatus.PASS):
    class StubEvaluator:
        def evaluate(self, *args):
            calls.append((metric_name, args))
            return make_metric_result(metric_name, status)

    return StubEvaluator


def patch_evaluators(monkeypatch, calls, statuses=None):
    """用 Stub 替代五个具体 Evaluator。"""
    statuses = statuses or {}

    evaluator_classes = {
        "IntentEvaluator": "intent_match",
        "ToolCallEvaluator": "tool_call_sequence",
        "ToolExecutionStatusEvaluator": "tool_execution_status",
        "BusinessStateEvaluator": "business_state_match",
        "ResponseEvaluator": "response_check",
    }

    for class_name, metric_name in evaluator_classes.items():
        stub_class = make_stub_class(
            metric_name,
            calls,
            statuses.get(metric_name, EvaluationStatus.PASS),
        )
        monkeypatch.setattr(
            evaluator_module,
            class_name,
            stub_class,
        )


def test_evaluate_calls_all_registered_evaluators(monkeypatch):
    calls = []
    patch_evaluators(monkeypatch, calls)

    evaluator = Evaluator()
    testcase = make_testcase([
        "intent_match",
        "tool_call_sequence",
        "tool_execution_status",
        "business_state_match",
        "response_check",
    ])

    agent_result = object()
    trace = object()

    report = evaluator.evaluate(testcase, agent_result, trace)

    assert len(calls) == 5
    assert len(report.results) == 5

    # 不同指标接收的参数数量不同
    for metric_name, args in calls:
        if metric_name in {
            "intent_match",
            "business_state_match",
            "response_check",
        }:
            assert len(args) == 2
        else:
            assert len(args) == 3

    assert report.status == EvaluationStatus.PASS


def test_evaluate_continues_when_one_metric_fails(monkeypatch):
    calls = []
    patch_evaluators(
        monkeypatch,
        calls,
        statuses={"intent_match": EvaluationStatus.FAIL},
    )

    evaluator = Evaluator()
    testcase = make_testcase([
        "intent_match",
        "business_state_match",
    ])

    report = evaluator.evaluate(testcase, object(), object())

    assert len(calls) == 2
    assert report.results[0].status == EvaluationStatus.FAIL
    assert report.results[1].status == EvaluationStatus.PASS
    assert report.status == EvaluationStatus.FAIL


def test_evaluate_unknown_metric_logs_warning_and_continues(
    monkeypatch, caplog
):
    calls = []
    patch_evaluators(monkeypatch, calls)

    evaluator = Evaluator()
    testcase = make_testcase([
        "unknown_metric",
        "intent_match",
    ])

    with caplog.at_level("WARNING"):
        report = evaluator.evaluate(testcase, object(), object())

    assert len(calls) == 1
    assert report.results[0].status == EvaluationStatus.BLOCKED
    assert report.results[1].status == EvaluationStatus.PASS
    assert "Unknown evaluation metric" in caplog.text


@pytest.mark.parametrize(
    "evaluation",
    [
        None,
        {},
        {"required_checks": None},
        {"required_checks": []},
        {"required_checks": "intent_match"},
        {"required_checks": [123]},
        {"required_checks": [""]},
    ],
)
def test_evaluate_invalid_required_checks_returns_blocked(evaluation):
    evaluator = Evaluator()
    testcase = testcase = make_testcase([evaluation
        ])

    report = evaluator.evaluate(testcase, object(), object())

    assert report.status == EvaluationStatus.BLOCKED
    assert len(report.results) == 1
    assert report.results[0].status == EvaluationStatus.BLOCKED
