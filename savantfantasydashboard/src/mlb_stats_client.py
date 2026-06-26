import requests
from typing import List, Dict, Optional


class MLBStatsClient:
    BASE_URL = "https://statsapi.mlb.com/api"

    def __init__(self, timeout: int = 10):
        self.session = requests.Session()
        self.timeout = timeout

    def _get(self, path: str, params: Dict = None) -> Dict:
        url = f"{self.BASE_URL}{path}"
        resp = self.session.get(url, params=params or {}, timeout=self.timeout)
        if resp.status_code != 200:
            raise Exception(f"MLB Stats API error {resp.status_code}: {resp.text}")
        return resp.json()

    # ---------- Player search ----------

    def search_player(self, name: str) -> List[Dict]:
        """
        Search players by name. Returns a list of basic matches.
        """
        data = self._get("/v1/people/search", params={"names": name})
        people = data.get("people", [])
        results = []
        for p in people:
            results.append({
                "id": p.get("id"),
                "full_name": p.get("fullName"),
                "first_name": p.get("firstName"),
                "last_name": p.get("lastName"),
                "primary_position": (p.get("primaryPosition") or {}).get("abbreviation"),
                "current_team_id": (p.get("currentTeam") or {}).get("id"),
            })
        return results

    # ---------- Player profile ----------

    def get_player_profile(self, player_id: int) -> Dict:
        """
        Get detailed player info (team, position, etc.).
        """
        data = self._get(f"/v1/people/{player_id}")
        people = data.get("people", [])
        if not people:
            raise Exception(f"No player found for id {player_id}")
        p = people[0]
        return {
            "id": p.get("id"),
            "full_name": p.get("fullName"),
            "first_name": p.get("firstName"),
            "last_name": p.get("lastName"),
            "primary_position": (p.get("primaryPosition") or {}).get("abbreviation"),
            "bat_side": (p.get("batSide") or {}).get("code"),
            "pitch_hand": (p.get("pitchHand") or {}).get("code"),
            "current_team_id": (p.get("currentTeam") or {}).get("id"),
            "mlb_debut_date": p.get("mlbDebutDate"),
        }

    # ---------- Season stats ----------

    def get_player_season_stats(
        self,
        player_id: int,
        season: int,
        stat_group: str = "hitting",
        stat_type: str = "season"
    ) -> Optional[Dict]:
        """
        Get season stats for a player.
        stat_group: 'hitting', 'pitching', 'fielding'
        stat_type: 'season', 'career', etc.
        """
        params = {
            "stats": stat_type,
            "group": stat_group,
            "season": season,
        }
        data = self._get(f"/v1/people/{player_id}/stats", params=params)
        splits = (data.get("stats") or [{}])[0].get("splits", [])
        if not splits:
            return None

        s = splits[0].get("stat", {})
        return {
            "season": season,
            "group": stat_group,
            "games": s.get("gamesPlayed"),
            "plate_appearances": s.get("plateAppearances"),
            "at_bats": s.get("atBats"),
            "hits": s.get("hits"),
            "doubles": s.get("doubles"),
            "triples": s.get("triples"),
            "home_runs": s.get("homeRuns"),
            "runs": s.get("runs"),
            "rbi": s.get("rbi"),
            "stolen_bases": s.get("stolenBases"),
            "caught_stealing": s.get("caughtStealing"),
            "walks": s.get("baseOnBalls"),
            "strikeouts": s.get("strikeOuts"),
            "avg": s.get("avg"),
            "obp": s.get("obp"),
            "slg": s.get("slg"),
            "ops": s.get("ops"),
        }

    # ---------- Game logs ----------

    def get_player_game_logs(
        self,
        player_id: int,
        season: int,
        stat_group: str = "hitting"
    ) -> List[Dict]:
        """
        Get per-game logs for a player in a given season.
        """
        params = {
            "stats": "gameLog",
            "group": stat_group,
            "season": season,
        }
        data = self._get(f"/v1/people/{player_id}/stats", params=params)
        splits = (data.get("stats") or [{}])[0].get("splits", [])
        logs = []
        for split in splits:
            stat = split.get("stat", {})
            game = split.get("date")
            logs.append({
                "date": game,
                "season": season,
                "group": stat_group,
                "games": stat.get("gamesPlayed"),
                "plate_appearances": stat.get("plateAppearances"),
                "at_bats": stat.get("atBats"),
                "hits": stat.get("hits"),
                "doubles": stat.get("doubles"),
                "triples": stat.get("triples"),
                "home_runs": stat.get("homeRuns"),
                "runs": stat.get("runs"),
                "rbi": stat.get("rbi"),
                "stolen_bases": stat.get("stolenBases"),
                "walks": stat.get("baseOnBalls"),
                "strikeouts": stat.get("strikeOuts"),
                "avg": stat.get("avg"),
                "obp": stat.get("obp"),
                "slg": stat.get("slg"),
                "ops": stat.get("ops"),
            })
        return logs
