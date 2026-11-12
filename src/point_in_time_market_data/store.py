"""Small, explicit as-of selection for revisioned point-in-time records."""

import math
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from numbers import Real


@dataclass(frozen=True)
class PointInTimeRecord:
    symbol: str
    field: str
    effective_at: date
    available_at: date
    value: float

    def __post_init__(self) -> None:
        if not isinstance(self.symbol, str) or not self.symbol.strip():
            raise ValueError("symbol must be a non-empty string")
        if not isinstance(self.field, str) or not self.field.strip():
            raise ValueError("field must be a non-empty string")
        if type(self.effective_at) is not date or type(self.available_at) is not date:
            raise ValueError("effective_at and available_at must be calendar dates")
        if self.available_at < self.effective_at:
            raise ValueError("available_at cannot precede effective_at")
        if isinstance(self.value, bool) or not isinstance(self.value, Real):
            raise TypeError("value must be a real number")
        value = float(self.value)
        if not math.isfinite(value):
            raise ValueError("value must be finite")
        object.__setattr__(self, "value", value)


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
    if type(as_of) is not date:
        raise ValueError("as_of must be a calendar date")
    if not isinstance(field, str) or not field.strip():
        raise ValueError("field must be a non-empty string")
    selected: dict[str, PointInTimeRecord] = {}
    for record in records:
        if not isinstance(record, PointInTimeRecord):
            raise TypeError("records must contain PointInTimeRecord values")
        if record.field != field:
            continue
        if record.effective_at > as_of or record.available_at > as_of:
            continue
        current = selected.get(record.symbol)
        record_key = (record.effective_at, record.available_at)
        current_key = None if current is None else (current.effective_at, current.available_at)
        if current is None or record_key > current_key:
            selected[record.symbol] = record
        elif record_key == current_key and record.value != current.value:
            raise ValueError("conflicting values share the same symbol and point-in-time dates")
    return {symbol: record.value for symbol, record in selected.items()}

