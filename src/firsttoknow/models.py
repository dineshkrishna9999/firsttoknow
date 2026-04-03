"""Data models for FirstToKnow."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any


class ItemType(StrEnum):
    """Type of item being tracked."""

    PYPI = "pypi"
    GITHUB = "github"
    TOPIC = "topic"
    NPM = "npm"


# ──────────────────────────────────────────────
# Guard models
# ──────────────────────────────────────────────


class Severity(StrEnum):
    """How serious is this finding?

    Why an enum instead of raw strings?
    - Prevents typos ("CRTICAL" would be caught at import time)
    - Enables comparison: Severity.CRITICAL > Severity.WARNING (StrEnum sorts alphabetically,
      but we use explicit ordering in GuardReport.grade)
    - IDE autocomplete works
    """

    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


@dataclass
class GuardFinding:
    """A single issue found during a guard scan.

    Think of this like one row in a report:
    - "requests has 2 known CVEs" → severity=CRITICAL
    - "colorama license changed MIT→GPL" → severity=CRITICAL
    - "httpx: no issues found" → severity=INFO

    Why a dataclass and not a dict?
    - Type safety: mypy catches if you misspell 'severity' as 'serverity'
    - Autocomplete: your IDE shows all fields
    - Immutability-friendly: easier to reason about
    """

    package: str
    ecosystem: str
    severity: Severity
    title: str
    details: str = ""
    url: str = ""


@dataclass
class GuardReport:
    """The full result of a guard scan.

    Contains all findings + a computed pass/fail verdict.
    """

    findings: list[GuardFinding] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        """Did the guard check pass? Fails if ANY critical finding exists."""
        return not any(f.severity == Severity.CRITICAL for f in self.findings)

    @property
    def critical_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == Severity.CRITICAL)

    @property
    def warning_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == Severity.WARNING)

    @property
    def info_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == Severity.INFO)

    @property
    def grade(self) -> str:
        """Compute a box-office verdict for the guard scan.

        Uses Indian box office classification — because code quality
        deserves the same drama as a Friday release 🎬:

            Blockbuster = no criticals, no warnings (clean as a ₹500cr hit)
            Superhit    = warnings but no criticals (still a winner)
            Hit         = 1 critical (one fix and you're golden)
            Average     = 2-3 criticals (needs work)
            Flop        = 4-5 criticals (not looking good)
            Disaster    = 6+ criticals (emergency fix needed)

        Why movie grades?
        ─────────────────
        Numbers and counts ("3 critical, 2 warnings") require mental math.
        A movie verdict gives instant gut-feel: Blockbuster = ship it, Disaster = fix it.
        """
        if self.critical_count == 0 and self.warning_count == 0:
            return "Blockbuster"
        if self.critical_count == 0:
            return "Superhit"
        if self.critical_count == 1:
            return "Hit"
        if self.critical_count <= 3:
            return "Average"
        if self.critical_count <= 5:
            return "Flop"
        return "Disaster"


@dataclass
class TrackedItem:
    """An item the user wants to track (package, repo, or topic)."""

    name: str
    item_type: ItemType
    source_url: str | None = None
    current_version: str | None = None
    added_at: datetime = field(default_factory=datetime.now)
    last_checked: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to a JSON-serializable dict."""
        data = asdict(self)
        data["item_type"] = self.item_type.value
        data["added_at"] = self.added_at.isoformat()
        data["last_checked"] = self.last_checked.isoformat() if self.last_checked else None
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TrackedItem:
        """Create from a dict (e.g. loaded from JSON)."""
        return cls(
            name=data["name"],
            item_type=ItemType(data["item_type"]),
            source_url=data.get("source_url"),
            current_version=data.get("current_version"),
            added_at=datetime.fromisoformat(data["added_at"]),
            last_checked=datetime.fromisoformat(data["last_checked"]) if data.get("last_checked") else None,
        )
