import csv

with open("data/fangraphs/hitting_061526.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    print(reader.fieldnames)
