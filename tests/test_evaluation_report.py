
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
        
def test_to_dict_returns_expected_structure():
    report = EvaluationReport(
        testcase_id="refund_success",
        results=(
            MetricResult(
                name="intent",
                status=EvaluationStatus.PASS,
                reason="意图符合预期",
                expected="refund",
                actual="refund",
            ),
            MetricResult(
                name="business_state",
                status=EvaluationStatus.PASS,
                reason="订单退款成功",
                expected="refunded",
                actual="refunded",
            ),
        ),
    )

    result = report.to_dict()

    assert result == {
        "testcase_id": "refund_success",
        "status": "PASS",
        "results": [
            {
                "name": "intent",
                "status": "PASS",
                "reason": "意图符合预期",
                "expected": "refund",
                "actual": "refund",
            },
            {
                "name": "business_state",
                "status": "PASS",
                "reason": "订单退款成功",
                "expected": "refunded",
                "actual": "refunded",
            },
        ],
    }


@pytest.mark.parametrize(
    ("results", "expected_status"),
    [
        ((), "BLOCKED"),
        (
            (
                MetricResult(
                    name="intent",
                    status=EvaluationStatus.FAIL,
                    reason="意图不符合预期",
                ),
            ),
            "FAIL",
        ),
        (
            (
                MetricResult(
                    name="intent",
                    status=EvaluationStatus.BLOCKED,
                    reason="缺少评测数据",
                ),
            ),
            "BLOCKED",
        ),
    ],
)
def test_to_dict_returns_correct_overall_status(results, expected_status):
    report = EvaluationReport(
        testcase_id="refund_test",
        results=results,
    )

    assert report.to_dict()["status"] == expected_status