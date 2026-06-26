# app.py
import streamlit as st
import traceback
from typing import Dict, Any, List, Optional

from src.league_statcast_builder import LeagueStatcastBuilder

st.set_page_config(
    page_title="Vlad the Impaler - 2026 Dashboard",
    layout="wide"
)

import numpy as np
import pandas as pd


def compute_metric_scores(players: Dict[str, Dict], side: str) -> Dict[str, float]:
    counts = {}
    values = {}
    total = len(players) or 1
    for p in players.values():
        metrics = p.get(side, {}) or {}
        for k, v in metrics.items():
            if v is None:
                continue
            counts.setdefault(k, 0)
            values.setdefault(k, []).append(v)
            counts[k] += 1

    scores = {}
    for k, vals in values.items():
        coverage = counts.get(k, 0) / total
        std = float(np.nanstd(vals)) if vals else 0.0
        scores[k] = coverage * std
    return dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))


def top_metrics_for_side(players: Dict[str, Dict], side: str, top_n: int = 12) -> List[str]:
    scores = compute_metric_scores(players, side)
    return [k for k, _ in list(scores.items())[:top_n]]


def player_top_percentile_metrics(player: Dict, side: str, top_n: int = 8) -> List[str]:
    pct = player.get("percentiles", {}).get(side, {}) or {}
    scored = []
    for k, v in pct.items():
        if v is None:
            continue
        try:
            scored.append((k, abs(float(v) - 50.0)))
        except Exception:
            continue
    scored.sort(key=lambda x: x[1], reverse=True)
    return [k for k, _ in scored[:top_n]]


FRIENDLY = {
    "avg_ev": "Avg EV",
    "max_ev": "Max EV",
    "hardhit_rate": "HardHit %",
    "barrel_rate": "Barrel %",
    "xwoba": "xwOBA",
    "xslg": "xSLG",
    "gb_pct": "GB %",
    "bat_run_value": "Bat Run Value",
    "pitch_run_value": "Pitch Run Value",
    "avg_ev_allowed": "Avg EV Allowed",
    "max_ev_allowed": "Max EV Allowed",
    "hardhit_rate_allowed": "HardHit % Allowed",
    "barrel_rate_allowed": "Barrel % Allowed",
    "chase_pct": "Chase %",
    "whiff_pct": "Whiff %",
    "k_pct": "K %",
    "bb_pct": "BB %",
    "era": "ERA",
    "xera": "xERA",
    "fip": "FIP",
    "ip": "IP",
    "pa": "PA",
}


def friendly_label(metric: str) -> str:
    if metric in FRIENDLY:
        return FRIENDLY[metric]
    s = metric.replace("_", " ").replace("pct", "%").replace("per", "/").strip()
    s = s.replace("ev", "EV").replace("la", "LA").replace("xwoba", "xwOBA").replace("xslg", "xSLG").replace("xba", "xBA")
    words = []
    for w in s.split():
        lw = w.lower()
        if lw in ("ip", "pa", "era", "fip", "woba", "ops", "avg", "slg", "obp", "so", "bb", "hr", "k/9", "bb/9", "whip"):
            words.append(w.upper())
        else:
            words.append(w.capitalize())
    return " ".join(words)


GROUP_MAP = {
    "Batted Ball Quality": ["avg_ev", "max_ev", "hardhit_rate", "barrel_rate"],
    "Expected Stats": ["xwoba", "xslg"],
    "Plate Discipline": ["chase_pct", "whiff_pct", "k_pct", "bb_pct"],
    "Run Prevention": ["era", "xera", "fip"],
    "Contact Quality Allowed": ["avg_ev_allowed", "max_ev_allowed", "hardhit_rate_allowed", "barrel_rate_allowed"],
    "Ground Balls": ["gb_pct"],
}


DEFAULT_TOP_HITTER_STATS = [
    "bat_run_value",
    "xwoba",
    "xslg",
    "avg_ev",
    "barrel_rate",
    "hardhit_rate",
    "chase_pct",
    "whiff_pct",
    "k_pct",
    "bb_pct",
]

DEFAULT_TOP_PITCHER_STATS = [
    "pitch_run_value",
    "xera",
    "avg_ev_allowed",
    "hardhit_rate_allowed",
    "gb_pct",
    "chase_pct",
    "whiff_pct",
    "k_pct",
    "bb_pct",
]


def percentile_color(p):
    if p is None:
        return "background-color: #444444; color: white;"
    x = float(p) / 100.0
    if x < 0.5:
        t = x / 0.5
        r = int(173 + (255 - 173) * t)
        g = int(216 + (255 - 216) * t)
        b = int(230 + (255 - 230) * t)
    else:
        t = (x - 0.5) / 0.5
        r = 255
        g = int(255 * (1 - t))
        b = int(255 * (1 - t))
    return f"background-color: rgb({r},{g},{b}); color: white;"


def render_player_card(summary: dict, role: str):
    is_hitter = bool(summary.get("hitting"))
    is_pitcher = bool(summary.get("pitching"))
    display_role = role or (("Hitter" if is_hitter else "") + (" / Pitcher" if is_pitcher else "")).strip() or "N/A"
    pa_ip = summary.get("hitting", {}).get("pa") if is_hitter else summary.get("pitching", {}).get("ip")
    pa_ip_label = "PA" if is_hitter else "IP"
    st.markdown(
        f"""
        <div style="
            padding: 16px;
            border-radius: 10px;
            background-color: #1e1e1e;
            color: white;
            margin-bottom: 12px;
        ">
            <h2 style="margin: 0; padding: 0;">{summary.get('name','Unknown')}</h2>
            <h4 style="margin: 0; padding: 0; opacity: 0.85;">
                {summary.get('team','')} &nbsp;•&nbsp; {display_role}
            </h4>
            <div style="margin-top: 8px; opacity: 0.9;">
                <b>{pa_ip_label}:</b> {pa_ip if pa_ip is not None else "–"}<br/>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_legend():
    st.markdown(
        """
        <div style="margin-bottom: 8px; color: white;">
            <b>Legend:</b>&nbsp;&nbsp;
            <span style="color:#ff4b4b;">Red</span> = High percentile &nbsp;•&nbsp;
            <span style="color:#add8e6;">Blue</span> = Low percentile
        </div>
        """,
        unsafe_allow_html=True
    )


def render_percentile_bars_grouped(percentiles: dict, is_hitter: bool, metrics_order: Optional[List[str]] = None):
    if not percentiles:
        st.write("No percentile data.")
        return
    render_legend()
    st.markdown("## Percentile Breakdown")
    if metrics_order:
        metrics = [m for m in metrics_order if m in percentiles]
        groups = {"Selected metrics": metrics}
    else:
        if is_hitter:
            groups = {
                "Batted Ball Quality": ["avg_ev", "max_ev", "hardhit_rate", "barrel_rate"],
                "Expected Stats": ["xwoba", "xslg"],
                "Plate Discipline": ["chase_pct", "whiff_pct", "k_pct", "bb_pct"],
                "Ground Balls": ["gb_pct"],
            }
        else:
            groups = {
                "Contact Quality Allowed": ["avg_ev_allowed", "max_ev_allowed", "hardhit_rate_allowed", "barrel_rate_allowed"],
                "Run Prevention": ["era", "xera", "fip"],
                "Plate Discipline": ["chase_pct", "whiff_pct", "k_pct", "bb_pct"],
                "Ground Balls": ["gb_pct"],
            }
        grouped_keys = {k for keys in groups.values() for k in keys}
        extras = [m for m in percentiles.keys() if m not in grouped_keys]
        if extras:
            groups["Other"] = extras
    for group_name, metrics in groups.items():
        st.markdown(f"### {group_name}")
        for metric in metrics:
            p = percentiles.get(metric)
            label = friendly_label(metric)
            value = f"{p:.1f}" if p is not None else "–"
            col1, col2, col3 = st.columns([1.5, 5, 1])
            col1.markdown(
                f"<div style='font-size:16px; font-weight:700; color:white;'>{label}</div>",
                unsafe_allow_html=True
            )
            if p is None:
                bar_html = "<div style='height:20px; background-color:#555; border-radius:6px;'></div>"
            else:
                width = max(2, min(100, float(p)))
                color = percentile_color(p).split("background-color: ")[1].split(";")[0]
                bar_html = f"""
                <div style="
                    background-color:{color};
                    height:20px;
                    width:{width}%;
                    border-radius:6px;
                    box-shadow:0 0 4px rgba(0,0,0,0.25);
                "></div>
                """
            col2.markdown(bar_html, unsafe_allow_html=True)
            col3.markdown(
                f"<div style='font-size:16px; font-weight:700; color:white;'>{value}</div>",
                unsafe_allow_html=True
            )


def build_player_index(players: dict) -> Dict[str, str]:
    index = {}
    for key, data in players.items():
        name = data.get("name") or f"player_{key}"
        if name in index:
            name = f"{name} ({key})"
        index[name] = key
    return index


def load_league_silent():
    try:
        builder = LeagueStatcastBuilder(
            scoring_path=r"C:\Users\njcer\OneDrive\Desktop\savantfantasydashboard\data\fantrax\scoring.csv",
            fg_hitting_path=r"C:\Users\njcer\OneDrive\Desktop\savantfantasydashboard\data\fangraphs\fg_hitting_all_061626.csv",
            fg_pitching_path=r"C:\Users\njcer\OneDrive\Desktop\savantfantasydashboard\data\fangraphs\fg_pitching_all_061626.csv",
            master_ids_path=r"C:\Users\njcer\OneDrive\Desktop\savantfantasydashboard\data\ids\master_ids.csv",
            cache_dir="data/cache",
            season=2026,
        )
        with st.spinner("Loading league + Statcast data…"):
            league = builder.build_league()
        return league
    except Exception:
        st.error("Failed to load league data. Check terminal for traceback.")
        st.text(traceback.format_exc())
        return None


@st.cache_data
def load_fantrax_scoring(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str).fillna("")
    df.columns = [c.strip() for c in df.columns]
    df.replace({"IFNA": "", "#N/A": "", "NA": "", "N/A": ""}, inplace=True)
    status_col = next((c for c in df.columns if c.lower() == "status"), None)
    if status_col is None:
        status_col = next((c for c in df.columns if "status" in c.lower()), None)
    if status_col:
        df["Status_norm"] = df[status_col].str.strip().str.lower()
    else:
        df["Status_norm"] = ""
    id_col = next((c for c in df.columns if c.lower() in ("id", "playerid", "fantraxid")), None)
    mlbam_col = next((c for c in df.columns if c.lower() in ("mlbamid", "mlbam", "key_mlbam")), None)
    df["_id_col"] = df[id_col] if id_col else ""
    df["_mlbam_col"] = df[mlbam_col] if mlbam_col else ""
    name_col = next((c for c in df.columns if c.lower() in ("player", "name")), None)
    team_col = next((c for c in df.columns if c.lower() in ("team", "teamname")), None)
    df["_player_name_norm"] = df[name_col].fillna("").str.strip().str.lower() if name_col else ""
    df["_team_norm"] = df[team_col].fillna("").str.strip().str.upper() if team_col else ""
    return df


def map_fantrax_to_player_keys(scoring_df: pd.DataFrame, players: dict) -> Dict[int, List[str]]:
    mapping: Dict[int, List[str]] = {}
    by_mlb: Dict[str, List[str]] = {}
    by_name_team: Dict[tuple, List[str]] = {}

    for key, p in players.items():
        mlb = str(p.get("mlbam_id") or p.get("mlbam") or "")
        if mlb:
            by_mlb.setdefault(mlb, []).append(key)
        nm = (p.get("name") or "").strip().lower()
        tm = (p.get("team") or "").strip().upper()
        if nm:
            by_name_team.setdefault((nm, tm), []).append(key)

    for idx, row in scoring_df.iterrows():
        mlbam = str(row.get("_mlbam_col", "")).strip()
        nm = str(row.get("_player_name_norm", "")).strip()
        tm = str(row.get("_team_norm", "")).strip()
        keys: List[str] = []

        if mlbam and mlbam in by_mlb:
            keys.extend(by_mlb[mlbam])

        if not keys and (nm, tm) in by_name_team:
            keys.extend(by_name_team[(nm, tm)])

        keys = list(dict.fromkeys(keys))
        mapping[idx] = keys

    return mapping


def render_roster_view(scoring_path: str, players: dict, default_status: str = "nc25"):
    scoring_df = load_fantrax_scoring(scoring_path)
    roster_df = scoring_df[scoring_df["Status_norm"] == default_status.lower()]
    if roster_df.empty:
        st.info(f"No players found with Status == {default_status}.")
        return

    mapping = map_fantrax_to_player_keys(scoring_df, players)

    st.header(f"Roster view Status = {default_status.upper()} ({len(roster_df)} players)")

    show_unmatched = st.sidebar.checkbox("Show unmatched rows", value=False, key="show_unmatched_rows_global")

    for idx, row in roster_df.iterrows():
        name = row.get("_player_name_norm", "").title()
        team = row.get("_team_norm", "")
        status = row.get("Status_norm", "")
        title = f"{name} — {team} — {status.upper()}"
        with st.expander(title, expanded=False):
            player_keys = mapping.get(idx, [])
            if not player_keys:
                st.write("Player not found in league mapping. Check master_ids or FanTrax mapping.")
                if show_unmatched:
                    st.json(row.to_dict())
                continue

            if len(player_keys) > 1:
                st.markdown(f"**Mapped to {len(player_keys)} players** — showing each below.")

            for pk in player_keys:
                p = players.get(pk)
                if not p:
                    st.write(f"Mapped key {pk} not found in players.")
                    continue

                st.markdown(f"**{p.get('name')} — {p.get('team')} — {p.get('position','N/A')}**")

                if p.get("hitting"):
                    pct = p.get("percentiles", {}).get("hitting", {}) or {}
                    top5 = [k for k in DEFAULT_TOP_HITTER_STATS if k in pct]
                    if not top5:
                        top5 = player_top_percentile_metrics(p, "hitting", top_n=5)
                    render_percentile_bars_grouped({k: pct.get(k) for k in top5 if k in pct}, True, metrics_order=top5)
                elif p.get("pitching"):
                    pct = p.get("percentiles", {}).get("pitching", {}) or {}
                    top5 = [k for k in DEFAULT_TOP_PITCHER_STATS if k in pct]
                    if not top5:
                        top5 = player_top_percentile_metrics(p, "pitching", top_n=5)
                    render_percentile_bars_grouped({k: pct.get(k) for k in top5 if k in pct}, False, metrics_order=top5)
                else:
                    st.write("No hitting or pitching data available for this player.")


def main():
    st.title("Vlad the Impaler - 2026 Dashboard")

    dev_mode = st.sidebar.checkbox("Developer mode (show debug)", value=False, key="dev_mode_global")

    if "top_hitter_stats" not in st.session_state:
        st.session_state.top_hitter_stats = DEFAULT_TOP_HITTER_STATS.copy()
    if "top_pitcher_stats" not in st.session_state:
        st.session_state.top_pitcher_stats = DEFAULT_TOP_PITCHER_STATS.copy()

    with st.sidebar.expander("Top stats configuration", expanded=False):
        st.sidebar.markdown("Edit the top stats shown for hitters and pitchers.")
        hitter_input = st.sidebar.text_area(
            "Hitter top stats (comma separated keys)",
            value=",".join(st.session_state.top_hitter_stats),
            height=80,
        )
        pitcher_input = st.sidebar.text_area(
            "Pitcher top stats (comma separated keys)",
            value=",".join(st.session_state.top_pitcher_stats),
            height=80,
        )
        st.session_state.top_hitter_stats = [s.strip() for s in hitter_input.split(",") if s.strip()]
        st.session_state.top_pitcher_stats = [s.strip() for s in pitcher_input.split(",") if s.strip()]

    league = load_league_silent()
    if not league:
        st.stop()

    players = league.get("players", {})
    if not players:
        st.warning("No players found in league. Check CSV parsing and master_ids mapping.")
        st.stop()

    if "global_hitting_top" not in st.session_state:
        st.session_state.global_hitting_top = top_metrics_for_side(players, "hitting", top_n=40)
        st.session_state.global_pitching_top = top_metrics_for_side(players, "pitching", top_n=40)

    scoring_path = r"C:\Users\njcer\OneDrive\Desktop\savantfantasydashboard\data\fantrax\scoring.csv"
    render_roster_view(scoring_path, players, default_status="nc25")

    player_index = build_player_index(players)
    selected_name = st.selectbox("Search player", sorted(player_index.keys()), key="player_search_selectbox")
    player_key = player_index[selected_name]
    player = players[player_key]

    ft_pos = None
    try:
        ft = player.get("fantrax") or {}
        if isinstance(ft, dict):
            ft_pos = ft.get("position") or ft.get("pos") or ft.get("Position")
    except Exception:
        ft_pos = None

    display_position = ft_pos or player.get("position") or (
        ("Hitter" if player.get("hitting") else "") + (" / Pitcher" if player.get("pitching") else "")
    ).strip() or "N/A"

    render_player_card(player, display_position)

    pct_h = player.get("percentiles", {}).get("hitting", {}) or {}
    pct_p = player.get("percentiles", {}).get("pitching", {}) or {}

    if player.get("hitting"):
        st.subheader("Hitting Metrics")
        configured_top = [k for k in st.session_state.top_hitter_stats if k in pct_h]
        top_keys = configured_top if configured_top else player_top_percentile_metrics(player, "hitting", top_n=8)
        if not top_keys:
            top_keys = list(pct_h.keys())[:8]
        render_percentile_bars_grouped({k: pct_h.get(k) for k in top_keys}, True, metrics_order=top_keys)
        remaining = [k for k in pct_h.keys() if k not in top_keys]
        remaining_sorted = [
            k for k in st.session_state.global_hitting_top if k in remaining
        ] + [k for k in remaining if k not in st.session_state.global_hitting_top]
        for group_name, pattern_keys in GROUP_MAP.items():
            group_metrics = [k for k in remaining_sorted if k in pattern_keys]
            if group_metrics:
                with st.expander(group_name, expanded=False):
                    render_percentile_bars_grouped(
                        {k: pct_h.get(k) for k in group_metrics}, True, metrics_order=group_metrics
                    )
        leftovers = [k for k in remaining_sorted if all(k not in v for v in GROUP_MAP.values())]
        if leftovers:
            with st.expander("Other Hitting Metrics", expanded=False):
                render_percentile_bars_grouped(
                    {k: pct_h.get(k) for k in leftovers}, True, metrics_order=leftovers
                )

    if player.get("pitching"):
        st.subheader("Pitching Metrics")
        configured_top_p = [k for k in st.session_state.top_pitcher_stats if k in pct_p]
        top_keys_p = configured_top_p if configured_top_p else player_top_percentile_metrics(player, "pitching", top_n=8)
        if not top_keys_p:
            top_keys_p = list(pct_p.keys())[:8]
        render_percentile_bars_grouped({k: pct_p.get(k) for k in top_keys_p}, False, metrics_order=top_keys_p)
        remaining_p = [k for k in pct_p.keys() if k not in top_keys_p]
        remaining_sorted_p = [
            k for k in st.session_state.global_pitching_top if k in remaining_p
        ] + [k for k in remaining_p if k not in st.session_state.global_pitching_top]
        for group_name, pattern_keys in GROUP_MAP.items():
            group_metrics = [k for k in remaining_sorted_p if k in pattern_keys]
            if group_metrics:
                with st.expander(group_name, expanded=False):
                    render_percentile_bars_grouped(
                        {k: pct_p.get(k) for k in group_metrics}, False, metrics_order=group_metrics
                    )
        leftovers_p = [k for k in remaining_sorted_p if all(k not in v for v in GROUP_MAP.values())]
        if leftovers_p:
            with st.expander("Other Pitching Metrics", expanded=False):
                render_percentile_bars_grouped(
                    {k: pct_p.get(k) for k in leftovers_p}, False, metrics_order=leftovers_p
                )

    if dev_mode:
        st.sidebar.markdown("### Developer Info")
        st.sidebar.write("Players loaded:", len(players))
        st.sidebar.write("Sample player key:", player_key)
        st.sidebar.write("Global hitting top (sample):", st.session_state.global_hitting_top[:20])
        st.sidebar.write("Global pitching top (sample):", st.session_state.global_pitching_top[:20])
        st.sidebar.write("Player raw hitting keys:", sorted(list(player.get("hitting", {}).keys()))[:80])
        st.sidebar.write("Player raw pitching keys:", sorted(list(player.get("pitching", {}).keys()))[:80])
        st.sidebar.write(
            "Player percentiles (hitting):",
            list(player.get("percentiles", {}).get("hitting", {}).items())[:40],
        )
        st.sidebar.write(
            "Player percentiles (pitching):",
            list(player.get("percentiles", {}).get("pitching", {}).items())[:40],
        )
        st.sidebar.markdown("---")
        st.sidebar.markdown("**Quick actions**")
        if st.sidebar.button("Recompute global metric scores", key="recompute_global_metrics"):
            st.session_state.global_hitting_top = top_metrics_for_side(players, "hitting", top_n=40)
            st.session_state.global_pitching_top = top_metrics_for_side(players, "pitching", top_n=40)
            st.experimental_rerun()

    st.markdown("---")
    st.markdown("**Next:** Toggle Developer mode to inspect raw keys. Ask to enable player comparison or team views.")


if __name__ == "__main__":
    main()
