
from pathlib import Path

import yaml

from agent_eval.models.test_case import TestCase


class TestCaseLoader:

    @staticmethod
    def load(file_path: str | Path) -> TestCase:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Test case file not found: {path}")

        with path.open("r", encoding="utf-8") as file:
            data = yaml.safe_load(file)

        if not isinstance(data, dict):
            raise ValueError(f"Invalid test case format: {path}")

        required_fields = [
            "case_id",
            "name",
            "description",
            "tags",
            "input",
            "fixtures",
            "expected",
            "evaluation",
        ]

        missing_fields = [
            field for field in required_fields
            if field not in data
        ]

        if missing_fields:
            raise ValueError(
                f"Missing required fields: {missing_fields}"
            )

        return TestCase(**data)
