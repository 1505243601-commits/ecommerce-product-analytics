from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "sample_events.csv"
OUTPUT_DIR = ROOT / "data" / "analytics"
FUNNEL_EVENTS = ["page_view", "prompt_submit", "generation_success", "result_adopt"]
REQUIRED_COLUMNS = ["event_date", "user_id", "session_id", "event_name", "feature", "model_version", "platform"]


def rate(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    return numerator.div(denominator.where(denominator.ne(0))).round(4)


def build_funnel(events: pd.DataFrame) -> pd.DataFrame:
    daily = (
        events[events["event_name"].isin(FUNNEL_EVENTS)]
        .pivot_table(index="event_date", columns="event_name", values="user_id", aggfunc="nunique", fill_value=0)
        .reindex(columns=FUNNEL_EVENTS, fill_value=0)
        .reset_index()
        .rename(columns={
            "page_view": "view_users",
            "prompt_submit": "submit_users",
            "generation_success": "success_users",
            "result_adopt": "adopt_users",
        })
    )
    daily["submit_rate"] = rate(daily["submit_users"], daily["view_users"])
    daily["generation_success_rate"] = rate(daily["success_users"], daily["submit_users"])
    daily["adoption_rate"] = rate(daily["adopt_users"], daily["success_users"])
    return daily


def build_quality_checks(events: pd.DataFrame) -> pd.DataFrame:
    missing_attributes = events[REQUIRED_COLUMNS].isna().sum().rename_axis("check_item").reset_index(name="issue_count")
    missing_attributes["check_type"] = "missing_attribute"
    duplicate_keys = ["event_date", "user_id", "session_id", "event_name", "feature"]
    duplicates = pd.DataFrame([{
        "check_type": "duplicate_event",
        "check_item": "event_date+user_id+session_id+event_name+feature",
        "issue_count": int(events.duplicated(duplicate_keys).sum()),
    }])
    unknown_events = pd.DataFrame([{
        "check_type": "unknown_event",
        "check_item": "event_name",
        "issue_count": int((~events["event_name"].isin(FUNNEL_EVENTS + ["feature_click"])).sum()),
    }])
    return pd.concat([missing_attributes[["check_type", "check_item", "issue_count"]], duplicates, unknown_events], ignore_index=True)


def main() -> None:
    if not INPUT.exists():
        raise FileNotFoundError(f"Sample data is missing: {INPUT}. Run generate_sample_events.py first.")
    events = pd.read_csv(INPUT, parse_dates=["event_date"])
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    build_funnel(events).to_csv(OUTPUT_DIR / "daily_funnel.csv", index=False)
    (
        events[events["event_name"] == "feature_click"]
        .groupby(["feature", "platform", "model_version"], as_index=False)
        .agg(active_users=("user_id", "nunique"), event_count=("event_name", "size"))
        .sort_values(["active_users", "event_count"], ascending=False)
        .to_csv(OUTPUT_DIR / "feature_usage.csv", index=False)
    )
    build_quality_checks(events).to_csv(OUTPUT_DIR / "data_quality_checks.csv", index=False)
    print(f"Wrote analytics outputs to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
