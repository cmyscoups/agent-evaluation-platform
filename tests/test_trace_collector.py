
import pytest

from agent_eval.collectors.trace_collector import TraceCollector


def test_collect_trace_with_two_spans():
    collector = TraceCollector()

    collector.start_trace("refund_success_001")

    # 记录查询订单
    collector.start_span("query_order")
    collector.add_event("tool_call_started")
    collector.add_event("tool_call_completed")
    collector.end_span()

    # 记录执行退款
    collector.start_span("refund_order")
    collector.add_event("tool_call_started")
    collector.add_event("tool_call_completed")
    collector.end_span()

    trace = collector.end_trace()

    assert trace.case_id == "refund_success_001"
    assert trace.status == "completed"
    assert trace.end_time is not None

    assert len(trace.spans) == 2

    assert trace.spans[0].name == "query_order"
    assert trace.spans[1].name == "refund_order"

    assert trace.spans[0].status == "success"
    assert len(trace.spans[0].events) == 2

    assert trace.spans[1].status == "success"
    assert len(trace.spans[1].events) == 2


def test_cannot_add_event_without_active_span():
    collector = TraceCollector()
    collector.start_trace("refund_success_001")

    with pytest.raises(RuntimeError):
        collector.add_event("tool_call_started")


def test_cannot_end_trace_with_active_span():
    collector = TraceCollector()
    collector.start_trace("refund_success_001")
    collector.start_span("query_order")

    with pytest.raises(RuntimeError):
        collector.end_trace()

def test_record_tool_call():
    collector = TraceCollector()
    collector.start_trace("case_001")
    span = collector.start_span("agent_execution")

    event = collector.record_tool_call(
        tool_name="query_order",
        arguments={"order_id": "ORDER_001"},
        status="success",
    )

    assert event.name == "tool_call"
    assert event.attributes == {
        "tool_name": "query_order",
        "arguments": {"order_id": "ORDER_001"},
        "status": "success",
    }

    assert span.events == [event]

def test_record_tool_call_without_active_span():
    collector = TraceCollector()
    collector.start_trace("case_001")

    with pytest.raises(RuntimeError, match="No active span"):
        collector.record_tool_call(
            tool_name="query_order",
            arguments={},
        )