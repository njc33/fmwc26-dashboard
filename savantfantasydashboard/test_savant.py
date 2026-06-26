from src.savant_client import SavantClient

def main():
    client = SavantClient()

    # Aaron Judge (MLBAM ID)
    player_id = 592450
    season = 2025

    print("Fetching Statcast event data...")
    events = client.get_statcast_data(player_id, season)
    print(f"Event rows fetched: {len(events)}")

    print("\nFetching Savant percentiles...")
    percentiles = client.get_player_percentiles(player_id, season)

    print("\nPercentiles received:")
    if percentiles:
        for k, v in percentiles.items():
            print(f"{k}: {v}")
    else:
        print("No percentile data returned (may not be published yet).")

    print("\nFetching Savant summary metrics...")
    summary = client.get_player_summary(player_id, season)

    print("\nSummary metrics:")
    if summary:
        for k, v in summary.items():
            print(f"{k}: {v}")
    else:
        print("No summary metrics returned.")

if __name__ == "__main__":
    main()
