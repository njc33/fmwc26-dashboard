from src.data_engine import DataEngine

def main():
    engine = DataEngine()

    # Test with Bregman + Kwan
    player_ids = [608324, 680757]  # Bregman, Kwan

    players = engine.load_players(player_ids, season=2024)

    for pid, player in players.items():
        print(f"\n=== {player.profile['full_name']} ===")
        print(player.to_dict())

if __name__ == "__main__":
    main()
