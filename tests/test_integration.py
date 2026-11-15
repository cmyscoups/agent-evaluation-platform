
from pathlib import Path

from agent_eval.case_loader import TestCaseLoader
from agent_eval.adapters.mock_agent import MockAgentAdapter
from agent_eval.collectors.trace_collector import TraceCollector
from agent_eval.evaluators.evaluator import Evaluator
from agent_eval.runner import EvaluationRunner
from agent_eval.models.evaluation_report import EvaluationStatus


def test_refund_success_integration():
    project_root = Path(__file__).resolve().parents[1]

    test_case = TestCaseLoader.load(
        project_root / "testcases" / "refund_success.yaml"
    )

    collector = TraceCollector()
    adapter = MockAgentAdapter(collector)
    evaluator = Evaluator()

    runner = EvaluationRunner(
        agent_adapter=adapter,
        evaluator=evaluator,
        collector=collector,
    )

    report = runner.run(test_case)
    # for result in report.results:
    #     print(
    #         result.name,
    #         result.status,
    #         result.reason,
    #     )
    # for span in runner.collector.get_trace().spans:
    #     print(
    #         "SPAN:",
    #         span.name,
    #         "STATUS:",
    #         span.status,
    #         "ATTRIBUTES:",
    #         span.attributes,
    #     )

    # 验证整体评测结果
    assert report.testcase_id == test_case.case_id
    assert report.status == EvaluationStatus.PASS

    # 验证五个评测指标全部通过
    assert len(report.results) == 5

    assert all(
        result.status == EvaluationStatus.PASS
        for result in report.results
    )

def test_refund_tool_failure_integration():
    project_root = Path(__file__).resolve().parents[1]

    test_case = TestCaseLoader.load(
        project_root / "testcases" / "refund_tool_failure.yaml"
    )

    collector = TraceCollector()
    adapter = MockAgentAdapter(collector)
    evaluator = Evaluator()

    runner = EvaluationRunner(
        agent_adapter=adapter,
        evaluator=evaluator,
        collector=collector,
    )

    report = runner.run(test_case)

    # 验证整体评测结果
    assert report.testcase_id == test_case.case_id
    assert report.status == EvaluationStatus.FAIL

    # 验证工具执行状态评测失败
    tool_status_result = next(
        result for result in report.results
        if result.name == "tool_execution_status"
    )
    assert tool_status_result.status == EvaluationStatus.FAIL

    # 验证其他指标仍然通过
    for result in report.results:
        if result.name != "tool_execution_status":
            assert result.status == EvaluationStatus.PASS
