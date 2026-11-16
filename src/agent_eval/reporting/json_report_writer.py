
import json
from pathlib import Path

from agent_eval.models.evaluation_report import EvaluationReport


class JsonReportWriter:

    def write(
        self,
        report: EvaluationReport,
        output_path: str | Path,
    ) -> Path:
        output_path = Path(output_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with output_path.open("w", encoding="utf-8") as file:
            json.dump(
                report.to_dict(),
                file,
                ensure_ascii=False,
                indent=2,
            )

        return output_path
