import requests
import csv
import io
from typing import List, Dict, Optional


class SavantClient:
    BASE_URL = "https://baseballsavant.mlb.com/statcast_search/csv"

    def __init__(self, timeout: int = 30):
        self.session = requests.Session()
        self.timeout = timeout

    def get_statcast_data(
        self,
        player_id: int,
        season: int,
        player_type: str = "batter"
    ) -> List[Dict]:
        """
        Event-level Statcast data for a single player + season.
        """
        params = {
            "player_type": player_type,
            "player_id": player_id,
            "season": season,
            "type": "details",
            "hfPT": "",
            "hfAB": "",
            "hfBB": "",
            "hfPR": "",
            "hfZ": "",
            "hfGT": "R|",
            "min_pa": "0",
            "min_pitches": "0",
            "min_results": "0",
        }

        resp = self.session.get(self.BASE_URL, params=params, timeout=self.timeout)
        resp.raise_for_status()

        reader = csv.DictReader(io.StringIO(resp.text))
        return [dict(row) for row in reader]

    def compute_hitter_summary(self, events: List[Dict]) -> Dict:
        """
        Very basic hitter summary from event-level data.
        You can expand this later with more precise formulas.
        """
        def to_float(x):
            try:
                return float(x)
            except:
                return None

        pa = 0
        barrels = 0
        hard_hits = 0
        evs = []

        for e in events:
            ev = to_float(e.get("launch_speed"))
            if e.get("events") in ("single", "double", "triple", "home_run", "field_out",
                                   "strikeout", "walk", "hit_by_pitch", "sac_fly", "sac_bunt"):
                pa += 1
            if e.get("barrel") == "1":
                barrels += 1
            if ev is not None:
                evs.append(ev)
                if ev >= 95:
                    hard_hits += 1

        avg_ev = sum(evs) / len(evs) if evs else None
        barrel_rate = barrels / pa if pa > 0 else None
        hardhit_rate = hard_hits / pa if pa > 0 else None

        return {
            "pa": pa,
            "avg_ev": avg_ev,
            "barrel_rate": barrel_rate,
            "hardhit_rate": hardhit_rate,
        }

    def compute_pitcher_summary(self, events: List[Dict]) -> Dict:
        """
        Very basic pitcher summary from event-level data.
        Again, you can expand later.
        """
        def to_float(x):
            try:
                return float(x)
            except:
                return None

        bf = 0
        k = 0
        bb = 0
        evs_allowed = []
        hard_hits_allowed = 0

        for e in events:
            bf += 1
            desc = (e.get("description") or "").lower()
            if "strikeout" in desc:
                k += 1
            if "walk" in desc:
                bb += 1
            ev = to_float(e.get("launch_speed"))
            if ev is not None:
                evs_allowed.append(ev)
                if ev >= 95:
                    hard_hits_allowed += 1

        avg_ev_allowed = sum(evs_allowed) / len(evs_allowed) if evs_allowed else None
        hardhit_rate_allowed = hard_hits_allowed / bf if bf > 0 else None
        k_rate = k / bf if bf > 0 else None
        bb_rate = bb / bf if bf > 0 else None

        return {
            "bf": bf,
            "avg_ev_allowed": avg_ev_allowed,
            "hardhit_rate_allowed": hardhit_rate_allowed,
            "k_rate": k_rate,
            "bb_rate": bb_rate,
        }
