
from datetime import datetime, timezone
from uuid import uuid4

from agent_eval.models.trace import Trace, Span, TraceEvent


def current_time() -> str:
    return datetime.now(timezone.utc).isoformat()


class TraceCollector:

    def __init__(self):
        self.trace = None
        self.active_span = None

    def start_trace(self, case_id: str) -> Trace:
        if self.trace is not None and self.trace.status == "running":
            raise RuntimeError("A trace is already running")

        self.trace = Trace(
            trace_id=str(uuid4()),
            case_id=case_id,
            start_time=current_time(),
        )

        self.active_span = None
        return self.trace

    def start_span(
        self,
        name: str,
        attributes: dict | None = None,
    ) -> Span:
        if self.trace is None or self.trace.status != "running":
            raise RuntimeError("No active trace")

        if self.active_span is not None:
            raise RuntimeError("A span is already running")

        span = Span(
            span_id=str(uuid4()),
            name=name,
            start_time=current_time(),
            attributes=attributes or {},
        )

        self.trace.spans.append(span)
        self.active_span = span
        return span

    def add_event(
        self,
        name: str,
        attributes: dict | None = None,
    ) -> TraceEvent:
        if self.active_span is None:
            raise RuntimeError("No active span")

        event = TraceEvent(
            event_id=str(uuid4()),
            name=name,
            timestamp=current_time(),
            attributes=attributes or {},
        )

        self.active_span.events.append(event)
        return event

    def end_span(self, status: str = "success") -> None:
        if self.active_span is None:
            raise RuntimeError("No active span")

        self.active_span.end_time = current_time()
        self.active_span.status = status
        self.active_span = None

    def end_trace(self, status: str = "completed") -> Trace:
        if self.trace is None or self.trace.status != "running":
            raise RuntimeError("No active trace")

        if self.active_span is not None:
            raise RuntimeError("Cannot end trace while a span is running")

        self.trace.end_time = current_time()
        self.trace.status = status
        return self.trace

    def get_trace(self) -> Trace:
        if self.trace is None:
            raise RuntimeError("No trace available")

        return self.trace
    def record_tool_call(
        self,
        tool_name: str,
        arguments: dict,
        status: str = "success",
    ) -> TraceEvent:
        return self.add_event(
            name="tool_call",
            attributes={
                "tool_name": tool_name,
                "arguments": arguments,
                "status": status,
            },
        )