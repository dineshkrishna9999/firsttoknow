"""Tests for firsttoknow data models."""

from datetime import datetime

from firsttoknow.models import GuardFinding, GuardReport, ItemType, Severity, TrackedItem


class TestTrackedItem:
    """Tests for TrackedItem dataclass."""

    def test_create_pypi_item(self) -> None:
        item = TrackedItem(name="litellm", item_type=ItemType.PYPI, current_version="1.40.0")
        assert item.name == "litellm"
        assert item.item_type == ItemType.PYPI
        assert item.current_version == "1.40.0"
        assert item.source_url is None
        assert item.last_checked is None

    def test_create_github_item(self) -> None:
        item = TrackedItem(
            name="BerriAI/litellm",
            item_type=ItemType.GITHUB,
            source_url="https://github.com/BerriAI/litellm",
        )
        assert item.item_type == ItemType.GITHUB
        assert item.source_url == "https://github.com/BerriAI/litellm"

    def test_create_topic_item(self) -> None:
        item = TrackedItem(name="AI agents", item_type=ItemType.TOPIC)
        assert item.item_type == ItemType.TOPIC

    def test_to_dict(self) -> None:
        now = datetime(2026, 3, 29, 12, 0, 0)
        item = TrackedItem(
            name="litellm",
            item_type=ItemType.PYPI,
            current_version="1.40.0",
            added_at=now,
        )
        data = item.to_dict()
        assert data["name"] == "litellm"
        assert data["item_type"] == "pypi"
        assert data["added_at"] == "2026-03-29T12:00:00"
        assert data["last_checked"] is None

    def test_from_dict_roundtrip(self) -> None:
        now = datetime(2026, 3, 29, 12, 0, 0)
        original = TrackedItem(
            name="litellm",
            item_type=ItemType.PYPI,
            current_version="1.40.0",
            added_at=now,
        )
        data = original.to_dict()
        restored = TrackedItem.from_dict(data)
        assert restored.name == original.name
        assert restored.item_type == original.item_type
        assert restored.current_version == original.current_version
        assert restored.added_at == original.added_at

    def test_from_dict_with_last_checked(self) -> None:
        data = {
            "name": "click",
            "item_type": "pypi",
            "current_version": "8.1.0",
            "added_at": "2026-03-29T10:00:00",
            "last_checked": "2026-03-29T12:00:00",
        }
        item = TrackedItem.from_dict(data)
        assert item.last_checked == datetime(2026, 3, 29, 12, 0, 0)


class TestItemType:
    """Tests for ItemType enum."""

    def test_values(self) -> None:
        assert ItemType.PYPI.value == "pypi"
        assert ItemType.GITHUB.value == "github"
        assert ItemType.TOPIC.value == "topic"

    def test_from_string(self) -> None:
        assert ItemType("pypi") == ItemType.PYPI
        assert ItemType("github") == ItemType.GITHUB


# ──────────────────────────────────────────────
# GuardReport grade tests
# ──────────────────────────────────────────────


def _finding(severity: Severity, n: int = 1) -> list[GuardFinding]:
    """Helper: create n findings with given severity."""
    return [
        GuardFinding(package=f"pkg-{i}", ecosystem="pypi", severity=severity, title=f"finding {i}")
        for i in range(n)
    ]


class TestGuardReportGrade:
    """Test the letter grade computation.

    Each test name matches the grade it's testing,
    so failures are immediately obvious.
    """

    def test_grade_a_empty_report(self) -> None:
        """No findings at all → A."""
        report = GuardReport()
        assert report.grade == "A"

    def test_grade_a_info_only(self) -> None:
        """Only INFO findings (all clean) → A."""
        report = GuardReport(findings=_finding(Severity.INFO, 3))
        assert report.grade == "A"

    def test_grade_b_warnings_only(self) -> None:
        """Warnings but no criticals → B."""
        report = GuardReport(findings=_finding(Severity.WARNING, 2))
        assert report.grade == "B"

    def test_grade_b_warnings_and_info(self) -> None:
        """Mix of warnings and info, no criticals → still B."""
        report = GuardReport(
            findings=_finding(Severity.WARNING, 1) + _finding(Severity.INFO, 2)
        )
        assert report.grade == "B"

    def test_grade_c_one_critical(self) -> None:
        """Exactly 1 critical → C."""
        report = GuardReport(findings=_finding(Severity.CRITICAL, 1))
        assert report.grade == "C"

    def test_grade_d_two_criticals(self) -> None:
        """2 criticals → D."""
        report = GuardReport(findings=_finding(Severity.CRITICAL, 2))
        assert report.grade == "D"

    def test_grade_d_three_criticals(self) -> None:
        """3 criticals → D (boundary)."""
        report = GuardReport(findings=_finding(Severity.CRITICAL, 3))
        assert report.grade == "D"

    def test_grade_f_four_criticals(self) -> None:
        """4 criticals → F."""
        report = GuardReport(findings=_finding(Severity.CRITICAL, 4))
        assert report.grade == "F"

    def test_grade_f_many_criticals(self) -> None:
        """10 criticals → F."""
        report = GuardReport(findings=_finding(Severity.CRITICAL, 10))
        assert report.grade == "F"

    def test_grade_with_mixed_severities(self) -> None:
        """Criticals + warnings + info — grade based on criticals only."""
        report = GuardReport(
            findings=(
                _finding(Severity.CRITICAL, 2)
                + _finding(Severity.WARNING, 3)
                + _finding(Severity.INFO, 5)
            )
        )
        assert report.grade == "D"  # 2 criticals → D
