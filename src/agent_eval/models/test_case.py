
from dataclasses import dataclass, field
from typing import Any


@dataclass
class TestCase:
    case_id: str
    name: str
    description: str
    tags: list[str]
    input: dict[str, Any]
    fixtures: dict[str, Any]
    expected: dict[str, Any]
    evaluation: dict[str, Any]
    mock_config: dict[str, Any] = field(default_factory=dict)
