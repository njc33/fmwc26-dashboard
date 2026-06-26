import csv
from typing import List, Dict


class FantraxCSVImporter:
    """
    A unified importer for Fantrax CSV exports:
    - Roster (multi-section: Hitting + Pitching)
    - League Settings (4-column format)
    - Scoring (12-column format)
    """

    # ---------------------------------------------------------
    # 1. ROSTER IMPORTER (multi-section: Hitting + Pitching)
    # ---------------------------------------------------------
    def load_roster(self, path: str) -> List[Dict]:
        """
        Load a Fantrax roster CSV with separate Hitting and Pitching sections.
        Returns a unified list of player dicts.
        """
        players = []
        current_section = None
        headers = None

        # Fantrax often exports UTF-8 with BOM → use utf-8-sig
        with open(path, newline='', encoding='utf-8-sig') as f:
            reader = csv.reader(f)

            for row in reader:
                # Skip completely empty rows
                if all(cell.strip() == "" for cell in row):
                    continue

                # Detect section headers ("Hitting", "Pitching")
                if len(row) > 1 and row[1].strip() in ("Hitting", "Pitching"):
                    current_section = row[1].strip()
                    headers = None  # next non-empty row becomes header
                    continue

                # Detect header row (first row after section header)
                if headers is None:
                    headers = row
                    continue

                # Normal data row
                data = {
                    headers[i]: row[i] if i < len(row) else ""
                    for i in range(len(headers))
                }
                data["Section"] = current_section  # Hitting or Pitching
                players.append(data)

        return players

    # ---------------------------------------------------------
    # 2. LEAGUE SETTINGS IMPORTER (4-column format)
    # ---------------------------------------------------------
    def load_league_settings(self, path: str) -> List[Dict]:
        """
        Load league settings with columns:
        Group, Category Name, Category Abbrv, Assign Points
        """
        settings = []

        with open(path, newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)

            for row in reader:
                settings.append({
                    "group": row.get("Group"),
                    "name": row.get("Category Name"),
                    "abbr": row.get("Category Abbrv"),
                    "points": float(row.get("Assign Points", 0)),
                })

        return settings

    # ---------------------------------------------------------
    # 3. SCORING IMPORTER (12-column format)
    # ---------------------------------------------------------
    def load_scoring(self, path: str) -> List[Dict]:
        """
        Load Fantrax scoring CSV with columns:
        ID, Player, Team, Position, RkOV, Status, Age, Contract,
        FPts, FP/G, Ros, +/-
        """
        scoring = []

        with open(path, newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)

            for row in reader:
                scoring.append({
                    "fantrax_id": row.get("ID"),
                    "name": row.get("Player"),
                    "team": row.get("Team"),
                    "positions": row.get("Position", "").split(","),
                    "rank_overall": row.get("RkOV"),
                    "status": row.get("Status"),
                    "age": row.get("Age"),
                    "contract": row.get("Contract"),
                    "fantasy_points": float(row.get("FPts", 0)),
                    "fantasy_points_per_game": float(row.get("FP/G", 0)),
                    "rostered_pct": row.get("Ros"),
                    "trend": row.get("+/-"),
                })

        return scoring
