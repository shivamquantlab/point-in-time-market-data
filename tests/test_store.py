from datetime import date, datetime

import pytest

from point_in_time_market_data import PointInTimeRecord, snapshot


def test_snapshot_excludes_later_publication_and_uses_restatement_as_of_date():
    records = [
        PointInTimeRecord("SYN", "sales", date(2024, 12, 31), date(2025, 2, 1), 10),
        PointInTimeRecord("SYN", "sales", date(2024, 12, 31), date(2025, 3, 1), 9),
        PointInTimeRecord("SYN", "sales", date(2025, 1, 31), date(2025, 2, 15), 12),
    ]
    assert snapshot(records, as_of=date(2025, 2, 20), field="sales") == {"SYN": 12}
    assert snapshot(records, as_of=date(2025, 2, 10), field="sales") == {"SYN": 10}


def test_empty_snapshot_and_field_filter():
    row = PointInTimeRecord("SYN", "sales", date(2025, 1, 1), date(2025, 1, 2), 1)
    assert snapshot([row], as_of=date(2025, 1, 3), field="earnings") == {}


def test_invalid_publication_order_is_rejected():
    with pytest.raises(ValueError, match="cannot precede"):
        PointInTimeRecord("SYN", "sales", date(2025, 2, 2), date(2025, 2, 1), 1)


def test_same_point_in_time_key_cannot_select_conflicting_values_by_input_order():
    available = date(2025, 2, 1)
    first = PointInTimeRecord("SYN", "sales", date(2025, 1, 31), available, 10)
    conflicting = PointInTimeRecord("SYN", "sales", date(2025, 1, 31), available, 11)
    with pytest.raises(ValueError, match="conflicting values"):
        snapshot([first, conflicting], as_of=date(2025, 2, 2), field="sales")


def test_datetime_is_rejected_in_daily_date_fields():
    with pytest.raises(ValueError, match="calendar dates"):
        PointInTimeRecord(
            "SYN", "sales", datetime(2025, 1, 31), date(2025, 2, 1), 10
        )


def test_snapshot_rejects_datetime_as_of_and_blank_field():
    row = PointInTimeRecord("SYN", "sales", date(2025, 1, 31), date(2025, 2, 1), 10)
    with pytest.raises(ValueError, match="as_of"):
        snapshot([row], as_of=datetime(2025, 2, 2), field="sales")
    with pytest.raises(ValueError, match="field"):
        snapshot([row], as_of=date(2025, 2, 2), field=" ")

