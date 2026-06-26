from typing import Dict, List, Optional


class Player:
    def __init__(
        self,
        player_id: int,
        profile: Dict,
        season_stats: Optional[Dict],
        statcast_events: List[Dict],
        fantasy: Optional[Dict] = None
    ):
        self.id = player_id
        self.profile = profile
        self.season_stats = season_stats
        self.statcast_events = statcast_events
        self.fantasy = fantasy or {}

        # Derived metrics
        self.barrel_rate = self._compute_barrel_rate()
        self.hard_hit_rate = self._compute_hard_hit_rate()
        self.avg_ev = self._compute_avg_ev()
        self.avg_la = self._compute_avg_la()

    # ---------- Derived Metrics ----------

    def _compute_barrel_rate(self) -> Optional[float]:
        if not self.statcast_events:
            return None
        barrels = sum(e["barrel"] for e in self.statcast_events)
        return barrels / len(self.statcast_events)

    def _compute_hard_hit_rate(self) -> Optional[float]:
        if not self.statcast_events:
            return None
        hard_hits = sum(1 for e in self.statcast_events if e["launch_speed"] and e["launch_speed"] >= 95)
        return hard_hits / len(self.statcast_events)

    def _compute_avg_ev(self) -> Optional[float]:
        evs = [e["launch_speed"] for e in self.statcast_events if e["launch_speed"]]
        return sum(evs) / len(evs) if evs else None

    def _compute_avg_la(self) -> Optional[float]:
        las = [e["launch_angle"] for e in self.statcast_events if e["launch_angle"]]
        return sum(las) / len(las) if las else None

    # ---------- Export ----------

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "profile": self.profile,
            "season_stats": self.season_stats,
            "fantasy": self.fantasy,
            "derived": {
                "barrel_rate": self.barrel_rate,
                "hard_hit_rate": self.hard_hit_rate,
                "avg_ev": self.avg_ev,
                "avg_la": self.avg_la,
            },
        }
