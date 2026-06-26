import requests

STATS_API = "https://statsapi.mlb.com/api/v1"

def get_mlb_player_ids(season: int):
    """
    Returns (hitter_ids, pitcher_ids) for all MLB players who appeared in the given season.
    """
    url = f"{STATS_API}/teams?sportId=1&season={season}"
    teams = requests.get(url).json()["teams"]

    hitter_ids = set()
    pitcher_ids = set()

    for team in teams:
        roster_url = f"{STATS_API}/teams/{team['id']}/roster?season={season}"
        roster = requests.get(roster_url).json().get("roster", [])

        for player in roster:
            pid = player["person"]["id"]
            pos = player["position"]["abbreviation"]

            if pos in ("P",):
                pitcher_ids.add(pid)
            else:
                hitter_ids.add(pid)

    return list(hitter_ids), list(pitcher_ids)
