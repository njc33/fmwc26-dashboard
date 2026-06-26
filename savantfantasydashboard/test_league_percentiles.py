from src.league_statcast_builder import LeagueStatcastBuilder

# MLBAMIDs you provided
TEST_MLBAM_IDS = [
    694819,
    671922,
    695578,
    665742,
    686948,
]

def main():
    season = 2026
    builder = LeagueStatcastBuilder(seasons=[season])

    print("Building or loading league summary...")
    league = builder.load_or_build_season(season)

    for mlbam_id in TEST_MLBAM_IDS:
        print(f"\n=== Player MLBAMID {mlbam_id} ===")

        # Look up by MLBAMID inside hitters first, then pitchers
        summary = None
        percentiles = None

        # Search hitters
        for pid, data in league["hitters"].items():
            if data.get("mlbam_id") == mlbam_id:
                summary = data
                percentiles = data.get("percentiles")
                role = "hitter"
                break

        # If not found, search pitchers
        if summary is None:
            for pid, data in league["pitchers"].items():
                if data.get("mlbam_id") == mlbam_id:
                    summary = data
                    percentiles = data.get("percentiles")
                    role = "pitcher"
                    break

        print("Summary:")
        print(summary)
        print("Percentiles:")
        print(percentiles)

if __name__ == "__main__":
    main()
