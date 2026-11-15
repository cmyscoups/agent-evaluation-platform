
import pytest
from dataclasses import FrozenInstanceError

from agent_eval.models.evaluation_report import (
    EvaluationReport,
    EvaluationStatus,
    MetricResult,
)


def create_metric(status):
    return MetricResult(
        name="test_metric",
        status=status,
        reason="test reason",
    )


def test_all_pass_returns_pass():
    report = EvaluationReport(
        testcase_id="case_001",
        results=[
            create_metric(EvaluationStatus.PASS),
            create_metric(EvaluationStatus.PASS),
        ],
    )

    assert report.status == EvaluationStatus.PASS


def test_any_fail_returns_fail():
    report = EvaluationReport(
        testcase_id="case_001",
        results=[
            create_metric(EvaluationStatus.PASS),
            create_metric(EvaluationStatus.FAIL),
        ],
    )

    assert report.status == EvaluationStatus.FAIL


def test_blocked_without_fail_returns_blocked():
    report = EvaluationReport(
        testcase_id="case_001",
        results=[
            create_metric(EvaluationStatus.PASS),
            create_metric(EvaluationStatus.BLOCKED),
        ],
    )

    assert report.status == EvaluationStatus.BLOCKED


def test_fail_and_blocked_returns_fail():
    report = EvaluationReport(
        testcase_id="case_001",
        results=[
            create_metric(EvaluationStatus.FAIL),
            create_metric(EvaluationStatus.BLOCKED),
        ],
    )

    assert report.status == EvaluationStatus.FAIL


def test_empty_results_returns_blocked():
    report = EvaluationReport(
        testcase_id="case_001",
        results=[],
    )

    assert report.status == EvaluationStatus.BLOCKED

def test_field_frozen():
    report = EvaluationReport(
        testcase_id="case_001",
        results=(create_metric(EvaluationStatus.PASS),),
    )

    # 不允许重新赋值
    with pytest.raises(FrozenInstanceError):
        report.testcase_id = "new_case_id"

    with pytest.raises(FrozenInstanceError):
        report.results = (create_metric(EvaluationStatus.FAIL),)

    # 不允许修改集合内容
    with pytest.raises(AttributeError):
        report.results.append(create_metric(EvaluationStatus.FAIL))
