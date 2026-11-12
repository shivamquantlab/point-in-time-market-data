"""Small, explicit as-of selection for revisioned point-in-time records."""

import math
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class PointInTimeRecord:
    symbol: str
    field: str
    effective_at: date
    available_at: date
    value: float

    def __post_init__(self) -> None:
        if not self.symbol or not self.field:
            raise ValueError("symbol and field must be non-empty")
        if self.available_at < self.effective_at:
            raise ValueError("available_at cannot precede effective_at")
        if not math.isfinite(self.value):
            raise ValueError("value must be finite")


def snapshot(
    records: Iterable[PointInTimeRecord],
    *,
    as_of: date,
    field: str,
) -> dict[str, float]:
    """Return each symbol's latest value knowable on as_of.

    Both economic effectiveness and publication availability must be no later
    than the decision date. Later restatements cannot rewrite an earlier view.
    """
    selected: dict[str, PointInTimeRecord] = {}
    for record in records:
        if record.field != field:
            continue
        if record.effective_at > as_of or record.available_at > as_of:
            continue
        current = selected.get(record.symbol)
        if current is None or (
            record.effective_at,
            record.available_at,
        ) > (current.effective_at, current.available_at):
            selected[record.symbol] = record
    return {symbol: record.value for symbol, record in selected.items()}

