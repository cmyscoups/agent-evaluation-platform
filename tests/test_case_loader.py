
from pathlib import Path

import pytest

from agent_eval.case_loader import TestCaseLoader


def test_load_refund_success_case():
    project_root = Path(__file__).resolve().parents[1]
    file_path = project_root / "testcases" / "refund_success.yaml"

    case = TestCaseLoader.load(file_path)

    assert case.case_id == "refund_success_001"
    assert case.name == "未发货订单退款成功"
    assert case.expected["intent"] == "refund"
    assert case.fixtures["orders"][0]["fulfillment_status"] == "unshipped"


def test_load_nonexistent_file():
    with pytest.raises(FileNotFoundError):
        TestCaseLoader.load("testcases/not_exists.yaml")
