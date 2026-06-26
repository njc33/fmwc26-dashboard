import requests

STATS_API = "https://statsapi.mlb.com/api/v1"


def get_hitter_summaries(season: int):
    """
    Returns a dict: { player_id: summary_dict }
    Summary includes xwOBA, xBA, xSLG, EV, HardHit%, Barrel%, K%, BB%, etc.
    """
    url = f"{STATS_API}/stats?stats=statcast&group=hitting&season={season}"
    data = requests.get(url).json()

    hitters = {}

    for row in data.get("stats", []):
        for player in row.get("splits", []):
            pid = player["player"]["id"]
            stat = player["stat"]

            hitters[pid] = {
                "xwoba": stat.get("xwOBA"),
                "xba": stat.get("xBA"),
                "xslg": stat.get("xSLG"),
                "avg_ev": stat.get("avgHitSpeed"),
                "hardhit_rate": stat.get("hardHitPercentage"),
                "barrel_rate": stat.get("barrelPercentage"),
                "k_rate": stat.get("strikeoutPercentage"),
                "bb_rate": stat.get("walkPercentage"),
                "whiff_rate": stat.get("whiffPercentage"),
                "chase_rate": stat.get("chasePercentage"),
            }

    return hitters


def get_pitcher_summaries(season: int):
    """
    Returns a dict: { player_id: summary_dict }
    Summary includes xwOBA-against, xBA-against, xSLG-against, EV allowed, etc.
    """
    url = f"{STATS_API}/stats?stats=statcast&group=pitching&season={season}"
    data = requests.get(url).json()

    pitchers = {}

    for row in data.get("stats", []):
        for player in row.get("splits", []):
            pid = player["player"]["id"]
            stat = player["stat"]

            pitchers[pid] = {
                "xwoba_against": stat.get("xwOBA"),
                "xba_against": stat.get("xBA"),
                "xslg_against": stat.get("xSLG"),
                "avg_ev_allowed": stat.get("avgHitSpeed"),
                "hardhit_rate_allowed": stat.get("hardHitPercentage"),
                "barrel_rate_allowed": stat.get("barrelPercentage"),
                "k_rate": stat.get("strikeoutPercentage"),
                "bb_rate": stat.get("walkPercentage"),
                "whiff_rate": stat.get("whiffPercentage"),
                "chase_rate": stat.get("chasePercentage"),
            }

    return pitchers
