
from pathlib import Path

from agent_eval.case_loader import TestCaseLoader
from agent_eval.adapters.mock_agent import MockAgentAdapter
from agent_eval.collectors.trace_collector import TraceCollector


def test_mock_agent_refund_success():
    project_root = Path(__file__).resolve().parents[1]

    test_case = TestCaseLoader.load(
        project_root / "testcases" / "refund_success.yaml"
    )

    collector = TraceCollector()
    adapter = MockAgentAdapter(collector)

    collector.start_trace(test_case.case_id)

    result = adapter.run(test_case)

    trace = collector.end_trace()

    # 验证 Agent 执行结果
    assert result.intent == "refund"
    assert result.response == "退款成功"

    assert [call.name for call in result.tool_calls] == [
        "query_order",
        "refund_order",
    ]

    assert result.final_state["refund_status"] == "refunded"

    # 验证原始测试数据没有被修改
    assert test_case.fixtures["orders"][0]["refund_status"] == "none"

    # 验证 Trace
    assert trace.case_id == test_case.case_id
    assert trace.status == "completed"
    assert len(trace.spans) == 2

    assert trace.spans[0].name == "query_order"
    assert trace.spans[1].name == "refund_order"

    # 每个工具调用都有开始和结束事件
    for span in trace.spans:
        assert span.status == "success"
        assert [event.name for event in span.events] == [
            "tool_call",
        ]
