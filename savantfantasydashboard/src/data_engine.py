from typing import List, Dict
from src.mlb_stats_client import MLBStatsClient
from src.savant_client import SavantClient
from src.player import Player
from src.fantrax_csv_importer import FantraxCSVImporter



class DataEngine:
    def __init__(self):
        self.mlb = MLBStatsClient()
        self.savant = SavantClient()
	self.fantrax = FantraxCSVImporter()

    def load_player(self, player_id: int, season: int = 2024) -> Player:
        """
        Fetch all data sources and return a unified Player object.
        """
        profile = self.mlb.get_player_profile(player_id)
        season_stats = self.mlb.get_player_season_stats(player_id, season)
        statcast_events = self.savant.get_statcast_data(player_id, season)

        return Player(
            player_id=player_id,
            profile=profile,
            season_stats=season_stats,
            statcast_events=statcast_events,
        )

    def load_players(self, player_ids: List[int], season: int = 2024) -> Dict[int, Player]:
        """
        Load multiple players and return a dict keyed by player_id.
        """
        players = {}
        for pid in player_ids:
            try:
                players[pid] = self.load_player(pid, season)
            except Exception as e:
                print(f"Error loading player {pid}: {e}")
        return players


	def load_fantrax_roster(self, path: str):
    		return self.fantrax.load_roster(path)

	def load_fantrax_scoring(self, path: str):
    		return self.fantrax.load_scoring(path)

