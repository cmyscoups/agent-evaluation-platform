
from dataclasses import dataclass
from enum import Enum
from typing import Any


class EvaluationStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class MetricResult:
    name: str
    status: EvaluationStatus
    reason: str
    expected: Any = None
    actual: Any = None


@dataclass(frozen=True)
class EvaluationReport:
    testcase_id: str
    results: tuple[MetricResult, ...]

    @property
    def status(self) -> EvaluationStatus:
        if not self.results:
            return EvaluationStatus.BLOCKED

        statuses = [result.status for result in self.results]

        if EvaluationStatus.FAIL in statuses:
            return EvaluationStatus.FAIL

        if EvaluationStatus.BLOCKED in statuses:
            return EvaluationStatus.BLOCKED

        return EvaluationStatus.PASS
