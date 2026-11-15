
from agent_eval.models.agent_result import AgentResult
from agent_eval.models.evaluation_report import EvaluationStatus
from agent_eval.models.test_case import TestCase
from agent_eval.evaluators.business_state_evaluator import (
    BusinessStateEvaluator,
)


def create_testcase(business_state=None):
    if business_state is None:
        business_state = {
            "order_id": "ORDER_001",
            "refund_status": "refunded",
        }

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
            "business_state": business_state,
        },
        evaluation={
            "required_checks": ["business_state_match"],
        },
    )


def create_agent_result(final_state=None):
    if final_state is None:
        final_state = {
            "order_id": "ORDER_001",
            "refund_status": "refunded",
        }

    return AgentResult(
        response="退款成功",
        intent="refund",
        final_state=final_state,
    )


def test_business_state_matches():
    evaluator = BusinessStateEvaluator()

    testcase = create_testcase()
    agent_result = create_agent_result()

    result = evaluator.evaluate(testcase, agent_result)

    assert result.status == EvaluationStatus.PASS
    assert result.name == "business_state_match"
    assert result.expected == {
        "order_id": "ORDER_001",
        "refund_status": "refunded",
    }
    assert result.actual == {
        "order_id": "ORDER_001",
        "refund_status": "refunded",
    }


def test_business_state_value_mismatch():
    evaluator = BusinessStateEvaluator()

    testcase = create_testcase()
    agent_result = create_agent_result({
        "order_id": "ORDER_001",
        "refund_status": "pending",
    })

    result = evaluator.evaluate(testcase, agent_result)

    assert result.status == EvaluationStatus.FAIL
    assert result.reason == (
        "Actual business state does not match expected state."
    )


def test_actual_business_state_missing_expected_field():
    evaluator = BusinessStateEvaluator()

    testcase = create_testcase()
    agent_result = create_agent_result({
        "order_id": "ORDER_001",
    })

    result = evaluator.evaluate(testcase, agent_result)

    assert result.status == EvaluationStatus.BLOCKED
    assert result.reason == (
        "Actual business state is missing expected fields."
    )


def test_actual_business_state_is_empty():
    evaluator = BusinessStateEvaluator()

    testcase = create_testcase()
    agent_result = create_agent_result({})

    result = evaluator.evaluate(testcase, agent_result)

    assert result.status == EvaluationStatus.BLOCKED
    assert result.reason == (
        "Actual business state is missing expected fields."
    )


def test_expected_business_state_is_missing():
    evaluator = BusinessStateEvaluator()

    testcase = create_testcase()
    testcase.expected.pop("business_state")

    agent_result = create_agent_result()

    result = evaluator.evaluate(testcase, agent_result)

    assert result.status == EvaluationStatus.BLOCKED
    assert result.reason == (
        "Expected business state is missing or invalid."
    )


def test_extra_actual_fields_do_not_affect_result():
    evaluator = BusinessStateEvaluator()

    testcase = create_testcase()
    agent_result = create_agent_result({
        "order_id": "ORDER_001",
        "refund_status": "refunded",
        "refund_amount": 100,
    })

    result = evaluator.evaluate(testcase, agent_result)

    assert result.status == EvaluationStatus.PASS
