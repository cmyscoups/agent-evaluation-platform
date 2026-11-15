
from dataclasses import dataclass, field
from typing import Any


@dataclass
class TraceEvent:
    event_id: str
    name: str
    timestamp: str
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass
class Span:
    span_id: str
    name: str
    start_time: str
    end_time: str | None = None
    status: str = "running"
    attributes: dict[str, Any] = field(default_factory=dict)
    events: list[TraceEvent] = field(default_factory=list)


@dataclass
class Trace:
    trace_id: str
    case_id: str
    start_time: str
    end_time: str | None = None
    status: str = "running"
    spans: list[Span] = field(default_factory=list)
