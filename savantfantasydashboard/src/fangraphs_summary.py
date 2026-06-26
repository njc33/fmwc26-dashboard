import csv
from typing import Dict, Optional


def _to_float(v: Optional[str]) -> Optional[float]:
    try:
        return float(v)
    except:
        return None


def load_hitter_summaries(season: int) -> Dict[int, Dict]:
    """
    Loads FanGraphs hitter Statcast summary CSV for the given season.
    Uses the exact columns provided by the user.
    """
    path = f"data/fangraphs/hitting_061526.csv"
    hitters: Dict[int, Dict] = {}

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            pid = int(row["PlayerId"])

            hitters[pid] = {
                "name": row["Name"],
                "team": row["Team"],
                "pa": _to_float(row["PA"]),
                "avg_ev": _to_float(row["EV"]),
                "hardhit_rate": _to_float(row["HardHit%"]),
                "barrel_rate": _to_float(row["Barrel%"]),
                "xba": _to_float(row["xBA"]),
                "xslg": _to_float(row["xSLG"]),
                "xwoba": _to_float(row["xwOBA"]),
                "k_rate": None,
                "bb_rate": None,
            }

    return hitters


def load_pitcher_summaries(season: int) -> Dict[int, Dict]:
    """
    Loads FanGraphs pitcher Statcast summary CSV for the given season.
    Uses the exact columns provided by the user.
    """
    path = f"data/fangraphs/pitching_061526.csv"
    pitchers: Dict[int, Dict] = {}

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            pid = int(row["PlayerId"])

            pitchers[pid] = {
                "name": row["Name"],
                "team": row["Team"],
                "ip": _to_float(row["IP"]),
                "avg_ev_allowed": _to_float(row["EV"]),
                "hardhit_rate_allowed": _to_float(row["HardHit%"]),
                "barrel_rate_allowed": _to_float(row["Barrel%"]),
                "xwoba_against": None,
                "k_rate": None,
                "bb_rate": None,
            }

    return pitchers
