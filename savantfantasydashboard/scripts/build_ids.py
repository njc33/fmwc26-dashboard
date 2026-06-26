import pandas as pd
from pybaseball import playerid_reverse_lookup

def build_master_id_table():
    # Load FanGraphs hitting & pitching CSVs
    hit = pd.read_csv("data/fangraphs/hitting_061526.csv")
    pit = pd.read_csv("data/fangraphs/pitching_061526.csv")

    # Extract unique MLBAM IDs
    ids = pd.concat([hit["MLBAMID"], pit["MLBAMID"]]).dropna().unique().tolist()

    # Reverse lookup
    id_table = playerid_reverse_lookup(ids, key_type="mlbam")

    # Save
    id_table.to_csv("data/ids/master_player_ids.csv", index=False)
    print("Saved master_player_ids.csv")

if __name__ == "__main__":
    build_master_id_table()
