
import json

from agent_eval.models.evaluation_report import (
    EvaluationReport,
    MetricResult,
    EvaluationStatus,
)
from agent_eval.reporting.json_report_writer import JsonReportWriter


def test_write_json_report(tmp_path):
    report = EvaluationReport(
        testcase_id="refund_success",
        results=(
            MetricResult(
                name="intent",
                status=EvaluationStatus.PASS,
                reason="意图符合预期",
                expected="refund",
                actual="refund",
            ),
            MetricResult(
                name="business_state",
                status=EvaluationStatus.PASS,
                reason="订单退款成功",
                expected="refunded",
                actual="refunded",
            ),
        ),
    )

    output_path = tmp_path / "reports" / "refund_success.json"

    writer = JsonReportWriter()
    result_path = writer.write(report, output_path)

    # 1. 检查文件是否生成
    assert result_path.exists()

    # 2. 检查文件内容是否正确
    with result_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    assert data == report.to_dict()

    # 3. 检查中文是否以正常文本保存
    content = result_path.read_text(encoding="utf-8")
    assert "订单退款成功" in content
