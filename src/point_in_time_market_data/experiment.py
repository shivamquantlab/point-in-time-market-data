"""Reproduce the synthetic revision example and save a chart."""

import argparse
import json
from datetime import date
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .store import PointInTimeRecord, snapshot


def synthetic_records() -> list[PointInTimeRecord]:
    """Hand-authored synthetic fundamentals; no real issuer data is used."""
    effective = date(2025, 1, 31)
    return [
        PointInTimeRecord("SYN-A", "revenue", effective, date(2025, 2, 10), 100.0),
        PointInTimeRecord("SYN-A", "revenue", effective, date(2025, 3, 3), 96.0),
        PointInTimeRecord("SYN-B", "revenue", effective, date(2025, 2, 14), 80.0),
        PointInTimeRecord("SYN-C", "revenue", effective, date(2025, 2, 25), 120.0),
    ]


def run(output_dir: Path) -> dict[str, float]:
    values = snapshot(synthetic_records(), as_of=date(2025, 2, 20), field="revenue")
    output_dir.mkdir(parents=True, exist_ok=True)
    symbols = sorted(values)
    fig, ax = plt.subplots(figsize=(6, 3.5))
    ax.bar(symbols, [values[symbol] for symbol in symbols], color="#2563eb")
    ax.set(title="Synthetic revenue knowable on 2025-02-20", ylabel="Synthetic units")
    ax.text(0.01, 0.98, "SYNTHETIC • later revision excluded",
            transform=ax.transAxes, va="top", fontsize=8)
    fig.tight_layout()
    fig.savefig(output_dir / "pit_snapshot.png", dpi=150)
    plt.close(fig)
    (output_dir / "summary.json").write_text(
        json.dumps({"as_of": "2025-02-20", "field": "revenue", "values": values}, indent=2) + "\n",
        encoding="utf-8",
    )
    return values


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("reports"))
    args = parser.parse_args()
    run(args.output_dir)
    print(f"Wrote synthetic point-in-time report to {args.output_dir}")


if __name__ == "__main__":
    main()

