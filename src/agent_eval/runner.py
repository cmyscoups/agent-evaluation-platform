from pathlib import Path

from agent_eval.adapters.base import AgentAdapter
from agent_eval.collectors.trace_collector import TraceCollector
from agent_eval.evaluators.evaluator import Evaluator
from agent_eval.reporting.json_report_writer import JsonReportWriter


class EvaluationRunner:

    def __init__(
        self,
        agent_adapter: AgentAdapter,
        evaluator: Evaluator,
        collector: TraceCollector,
        report_writer: JsonReportWriter | None = None,
    ):
        self.agent_adapter = agent_adapter
        self.evaluator = evaluator
        self.collector = collector
        self.report_writer = report_writer


    def run(self, test_case, output_path: str | Path | None = None):
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

        if output_path is not None:
            if self.report_writer is None:
                raise ValueError(
                    "output_path was provided, but report_writer is not configured"
                )

            self.report_writer.write(report, output_path)

        return report
