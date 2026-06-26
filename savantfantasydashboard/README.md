# savantfantasydashboard

**Part of the [fmwc26-dashboard](https://github.com/njc33/fmwc26-dashboard) project.**

A Statcast/Savant-powered analytics module that feeds the **Future GMs of America**
tab of the FMWC26 dashboard. It ingests MLB performance data from Baseball Savant
and surfaces actionable fantasy-relevant metrics for scouting, roster decisions,
and draft prep.

---

## Purpose

- **Data ingestion** – pulls Statcast, leaderboard, and player data via public APIs
- **Feature engineering** – xwOBA, barrel rate, sprint speed percentiles, K%/BB% trends
- **Dashboard data layer** – exports clean CSV/Parquet snapshots for the frontend tab

---

## Data Sources

| Source | Access method | Notes |
|---|---|---|
| Baseball Savant (Statcast) | pybaseball.statcast() | Public; no API key |
| FanGraphs leaderboards | pybaseball.fg_batting_data() | Public |
| Custom proprietary data | See Proprietary Data section | NOT committed |

---

## Project Structure

