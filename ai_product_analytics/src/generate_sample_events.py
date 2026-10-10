from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "sample_events.csv"
EVENT_FIELDS = ["event_date", "user_id", "session_id", "event_name", "feature", "model_version", "platform"]


def add_event(rows: list[dict[str, str]], event_date: date, user_id: str, session_id: str, event_name: str, feature: str, model_version: str, platform: str) -> None:
    rows.append({
        "event_date": event_date.isoformat(),
        "user_id": user_id,
        "session_id": session_id,
        "event_name": event_name,
        "feature": feature,
        "model_version": model_version,
        "platform": platform,
    })


def main() -> None:
    randomizer = random.Random(20261010)
    rows: list[dict[str, str]] = []
    start_date = date(2026, 8, 1)
    features = ["智能问答", "文案生成", "表格分析"]
    platforms = ["web", "desktop"]
    versions = ["v1", "v2"]

    for offset in range(45):
        current_date = start_date + timedelta(days=offset)
        for user_number in range(1, 181):
            if randomizer.random() > 0.58:
                continue
            user_id = f"u_{user_number:03d}"
            session_id = f"{current_date:%Y%m%d}_{user_id}"
            feature = randomizer.choice(features)
            platform = randomizer.choice(platforms)
            version = randomizer.choice(versions)
            add_event(rows, current_date, user_id, session_id, "page_view", feature, version, platform)
            if randomizer.random() < 0.72:
                add_event(rows, current_date, user_id, session_id, "prompt_submit", feature, version, platform)
            else:
                continue
            if randomizer.random() < 0.91:
                add_event(rows, current_date, user_id, session_id, "generation_success", feature, version, platform)
            else:
                continue
            if randomizer.random() < 0.46:
                add_event(rows, current_date, user_id, session_id, "result_adopt", feature, version, platform)
            if randomizer.random() < 0.54:
                add_event(rows, current_date, user_id, session_id, "feature_click", feature, version, platform)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=EVENT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} synthetic events to {OUTPUT}")


if __name__ == "__main__":
    main()
