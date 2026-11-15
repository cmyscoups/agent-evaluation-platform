
from agent_eval.models.agent_result import AgentResult
from agent_eval.models.evaluation_report import EvaluationStatus
from agent_eval.models.test_case import TestCase
from agent_eval.evaluators.response_evaluator import ResponseEvaluator


def create_testcase(must_include=None):
    if must_include is None:
        must_include = ["退款成功", "ORDER_001"]

    return TestCase(
        case_id="refund_001",
        name="Refund order",
        description="Test refund response",
        tags=["refund"],
        input={"message": "申请退款"},
        fixtures={},
        expected={
            "intent": "refund",
            "tool_calls": ["query_order", "refund_order"],
            "response": {
                "must_include": must_include,
            },
        },
        evaluation={
            "required_checks": ["response_check"],
        },
    )


def create_agent_result(response="退款成功，订单 ORDER_001 已提交退款。"):
    return AgentResult(
        response=response,
        intent="refund",
        tool_calls=[],
        final_state={},
    )


def test_response_contains_all_required_content():
    evaluator = ResponseEvaluator()

    testcase = create_testcase()
    agent_result = create_agent_result()

    result = evaluator.evaluate(testcase, agent_result)

    assert result.status == EvaluationStatus.PASS
    assert result.name == "response_check"
    assert result.expected == ["退款成功", "ORDER_001"]
    assert result.actual == "退款成功，订单 ORDER_001 已提交退款。"


def test_response_missing_one_required_content():
    evaluator = ResponseEvaluator()

    testcase = create_testcase()
    agent_result = create_agent_result(
        "退款成功，您的订单已经处理。"
    )

    result = evaluator.evaluate(testcase, agent_result)

    assert result.status == EvaluationStatus.FAIL
    assert result.actual["missing_items"] == ["ORDER_001"]


def test_response_missing_multiple_required_content():
    evaluator = ResponseEvaluator()

    testcase = create_testcase()
    agent_result = create_agent_result(
        "您的订单已经处理。"
    )

    result = evaluator.evaluate(testcase, agent_result)

    assert result.status == EvaluationStatus.FAIL
    assert result.actual["missing_items"] == [
        "退款成功",
        "ORDER_001",
    ]


def test_actual_response_is_none():
    evaluator = ResponseEvaluator()

    testcase = create_testcase()
    agent_result = create_agent_result(None)

    result = evaluator.evaluate(testcase, agent_result)

    assert result.status == EvaluationStatus.BLOCKED
    assert result.reason == "Actual response is missing or invalid."


def test_expected_must_include_is_missing():
    evaluator = ResponseEvaluator()

    testcase = create_testcase()
    testcase.expected["response"].pop("must_include")

    agent_result = create_agent_result()

    result = evaluator.evaluate(testcase, agent_result)

    assert result.status == EvaluationStatus.BLOCKED
    assert result.reason == (
        "Expected must_include configuration is missing or invalid."
    )


def test_expected_must_include_is_empty():
    evaluator = ResponseEvaluator()

    testcase = create_testcase(must_include=[])
    agent_result = create_agent_result()

    result = evaluator.evaluate(testcase, agent_result)

    assert result.status == EvaluationStatus.BLOCKED
    assert result.reason == (
        "Expected must_include configuration is missing or invalid."
    )


def test_extra_content_does_not_affect_result():
    evaluator = ResponseEvaluator()

    testcase = create_testcase()
    agent_result = create_agent_result(
        "您好！退款成功，订单 ORDER_001 已提交退款。"
        "预计到账时间为 3-5 个工作日。"
    )

    result = evaluator.evaluate(testcase, agent_result)

    assert result.status == EvaluationStatus.PASS
