from src.mlb_stats_client import MLBStatsClient
from src.savant_client import SavantClient
from src.player import Player

def main():
    mlb = MLBStatsClient()
    savant = SavantClient()

    # Alex Bregman
    pid = 608324

    profile = mlb.get_player_profile(pid)
    stats = mlb.get_player_season_stats(pid, 2024)
    events = savant.get_statcast_data(pid, 2024)

    player = Player(pid, profile, stats, events)

    print(player.to_dict())

if __name__ == "__main__":
    main()
