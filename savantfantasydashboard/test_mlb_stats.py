from src.mlb_stats_client import MLBStatsClient

def main():
    client = MLBStatsClient()

    results = client.search_player("Willson Contreras")
    print("Search results:", results)

    if results:
        pid = results[0]["id"]
        profile = client.get_player_profile(pid)
        print("Profile:", profile)

        stats = client.get_player_season_stats(pid, 2026)
        print("Season stats:", stats)

if __name__ == "__main__":
    main()
