from agent_eval.adapters.base import AgentAdapter
from agent_eval.collectors.trace_collector import TraceCollector
from agent_eval.evaluators.evaluator import Evaluator


class EvaluationRunner:

    def __init__(
        self,
        agent_adapter: AgentAdapter,
        evaluator: Evaluator,
        collector: TraceCollector,
    ):
        self.agent_adapter = agent_adapter
        self.evaluator = evaluator
        self.collector = collector


    def run(self, test_case):
        self.collector.start_trace(test_case.case_id)

        try:
            agent_result = self.agent_adapter.run(test_case)

        except Exception:
            if self.collector.active_span is not None:
                self.collector.end_span(status="failed")

            self.collector.end_trace(status="failed")
            raise

        trace = self.collector.end_trace(status="completed")

        report = self.evaluator.evaluate(
            test_case,
            agent_result,
            trace,
        )

        return report
