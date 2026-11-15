from abc import ABC, abstractmethod

from agent_eval.models.test_case import TestCase
from agent_eval.models.agent_result import AgentResult


class AgentAdapter(ABC):

    @abstractmethod
    def run(self, test_case: TestCase) -> AgentResult:
        """Execute an agent and return a normalized result."""
        pass