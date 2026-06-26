import json
import os

import streamlit as st

from src.league_statcast_builder import LeagueStatcastBuilder

NICK_KURTZ_ID = 702878
AARON_JUDGE_ID = 592450
GERRIT_COLE_ID = 543037


def load_league(season: int):
    builder = LeagueStatcastBuilder(seasons=[season])
    hitter_ids = [NICK_KURTZ_ID, AARON_JUDGE_ID]
    pitcher_ids = [GERRIT_COLE_ID]
    return builder, builder.load_or_build_season(season, hitter_ids, pitcher_ids)


def main():
    st.title("Fantasy Statcast Percentile Dashboard")

    season = st.selectbox("Season", [2025])
    builder, league = load_league(season)

    st.header("Hitters")
    for pid, name in [(NICK_KURTZ_ID, "Nick Kurtz"), (AARON_JUDGE_ID, "Aaron Judge")]:
        st.subheader(name)
        pct = builder.get_player_percentiles(league, pid, role="hitter") or {}
        st.write(pct)

    st.header("Pitchers")
    for pid, name in [(GERRIT_COLE_ID, "Gerrit Cole")]:
        st.subheader(name)
        pct = builder.get_player_percentiles(league, pid, role="pitcher") or {}
        st.write(pct)


if __name__ == "__main__":
    main()
