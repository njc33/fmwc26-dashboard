from src.fantrax_csv_importer import FantraxCSVImporter

def main():
    importer = FantraxCSVImporter()

    # Load your roster and scoring CSVs
    roster = importer.load_roster("data/fantrax/roster.csv")
    scoring = importer.load_scoring("data/fantrax/scoring.csv")

    # Extract your Fantrax IDs from the roster file
    # NOTE: roster rows use the header names from your CSV
    my_ids = {p.get("ID") for p in roster if p.get("ID")}

    # Filter scoring to only your players
    my_scoring = [row for row in scoring if row["fantrax_id"] in my_ids]

    # Print samples
    print("Roster sample:", roster[:3])
    print("My scoring sample:", my_scoring[:3])
    print("Total players on my team:", len(my_scoring))

if __name__ == "__main__":
    main()

