
import pytest

from agent_eval.evaluators.intent_evaluator import IntentEvaluator
from agent_eval.models.agent_result import AgentResult
from agent_eval.models.evaluation_report import EvaluationStatus
from agent_eval.models.test_case import TestCase


@pytest.fixture
def evaluator():
    return IntentEvaluator()


def create_testcase(intent="refund"):
    return TestCase(
        case_id="case_001",
        name="test refund",
        description="test intent evaluation",
        tags=[],
        input={},
        fixtures={},
        expected={"intent": intent},
        evaluation={},
    )


def create_agent_result(intent):
    return AgentResult(
        response="test response",
        intent=intent,
    )


def test_intent_match_returns_pass(evaluator):
    result = evaluator.evaluate(
        create_testcase("refund"),
        create_agent_result("refund"),
    )

    assert result.status == EvaluationStatus.PASS


def test_intent_mismatch_returns_fail(evaluator):
    result = evaluator.evaluate(
        create_testcase("refund"),
        create_agent_result("query_order"),
    )

    assert result.status == EvaluationStatus.FAIL


def test_missing_actual_intent_returns_blocked(evaluator):
    result = evaluator.evaluate(
        create_testcase("refund"),
        create_agent_result(None),
    )

    assert result.status == EvaluationStatus.BLOCKED


def test_missing_expected_intent_returns_blocked(evaluator):
    result = evaluator.evaluate(
        create_testcase(None),
        create_agent_result("refund"),
    )

    assert result.status == EvaluationStatus.BLOCKED
