```python
"""
fetch_data_from_apis.py
-----------------------
Pulls non-proprietary MLB Statcast and FanGraphs data via pybaseball
and writes clean snapshots to the data/ directory.

Usage:
    pip install pybaseball pandas
    python scripts/fetch_data_from_apis.py

Outputs (written to data/):
    statcast_latest.csv       - Statcast batter-level data (current season)
    fg_batting_leaders.csv    - FanGraphs batting leaderboard
    fg_pitching_leaders.csv   - FanGraphs pitching leaderboard
    sprint_speed.csv          - Sprint speed leaderboard (Baseball Savant)
"""

import os
import datetime
import pandas as pd

try:
    from pybaseball import (
        statcast,
        fg_batting_data,
        fg_pitching_data,
        statcast_running_splits,
        cache,
    )
except ImportError:
    raise ImportError("Run: pip install pybaseball")

# ── Config ────────────────────────────────────────────────────────────────────

CURRENT_YEAR = datetime.date.today().year
SEASON_START = f"{CURRENT_YEAR}-03-20"
TODAY        = datetime.date.today().isoformat()

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)

cache.enable()  # avoid redundant network requests


# ── Helpers ───────────────────────────────────────────────────────────────────

def save(df: pd.DataFrame, filename: str) -> None:
    path = os.path.join(DATA_DIR, filename)
    df.to_csv(path, index=False)
    print(f"  v Saved {len(df):,} rows -> {path}")


# ── Ingestion ─────────────────────────────────────────────────────────────────

def fetch_statcast(start: str = SEASON_START, end: str = TODAY) -> pd.DataFrame:
    print(f"[statcast] Fetching {start} -> {end} ...")
    df = statcast(start_dt=start, end_dt=end)
    batter_agg = (
        df.groupby(["batter", "player_name"])
        .agg(
            PA=("pitch_type", "count"),
            barrel_rate=("launch_speed_angle", lambda x: (x == 6).mean()),
            xwoba=("estimated_woba_using_speedangle", "mean"),
            exit_velocity_avg=("launch_speed", "mean"),
            launch_angle_avg=("launch_angle", "mean"),
            hard_hit_rate=("launch_speed", lambda x: (x >= 95).mean()),
        )
        .reset_index()
    )
    batter_agg["fetch_date"] = TODAY
    return batter_agg


def fetch_fg_batting(min_pa: int = 100) -> pd.DataFrame:
    print("[fangraphs] Fetching batting leaderboard ...")
    df = fg_batting_data(CURRENT_YEAR, CURRENT_YEAR, qual=min_pa)
    df["fetch_date"] = TODAY
    return df


def fetch_fg_pitching(min_ip: int = 20) -> pd.DataFrame:
    print("[fangraphs] Fetching pitching leaderboard ...")
    df = fg_pitching_data(CURRENT_YEAR, CURRENT_YEAR, qual=min_ip)
    df["fetch_date"] = TODAY
    return df


def fetch_sprint_speed() -> pd.DataFrame:
    print("[statcast] Fetching sprint speed leaderboard ...")
    df = statcast_running_splits(CURRENT_YEAR)
    df["fetch_date"] = TODAY
    return df


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  savantfantasydashboard — API data ingestion")
    print(f"  Run date : {TODAY}  |  Season: {CURRENT_YEAR}")
    print("=" * 60)

    steps = [
        ("statcast_latest.csv",    fetch_statcast),
        ("fg_batting_leaders.csv", fetch_fg_batting),
        ("fg_pitching_leaders.csv",fetch_fg_pitching),
        ("sprint_speed.csv",       fetch_sprint_speed),
    ]
    for filename, fn in steps:
        try:
            save(fn(), filename)
        except Exception as e:
            print(f"  X {filename} failed: {e}")

    print("\nDone! Check the data/ folder.")
    print("Tip: data/*.csv is gitignored — commit only curated outputs.")


if __name__ == "__main__":
    main()