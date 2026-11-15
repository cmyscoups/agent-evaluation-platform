from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolCall:
    name: str
    arguments: dict[str, Any]
    status: str = "success"


@dataclass
class AgentResult:
    response: str
    intent: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    final_state: dict[str, Any] = field(default_factory=dict)