# src/league_statcast_builder.py
"""
LeagueStatcastBuilder

Option C Statcast integration with fallback:
- Loads FanTrax scoring CSV and FanGraphs hitting/pitching CSVs
- For each league player, fetches Statcast data via pybaseball.statcast(player_id=mlbam)
- Resolves MLBAM via:
    1) key_mlbam
    2) Fangraphs ID (player_id_hitting/pitching) via playerid_reverse_lookup
    3) Name lookup via playerid_lookup
- Computes player-level Statcast summaries (hitting & pitching)
- Merges Statcast metrics into unified player objects
- Prefers FanTrax mapping by key_mlbam/key_fangraphs when attaching roster metadata
- Falls back to name/team mapping
- Computes percentiles for all numeric metrics per side (hitting/pitching)
- Writes audit CSVs:
    - data/cache/unmatched_players.csv (scoring rows that did not map to any player)
    - data/cache/unmatched_statcast_players.csv (players with no Statcast data)
    - data/cache/duplicate_mlbam_players.csv (duplicate key_mlbam occurrences)
    - data/cache/duplicate_ids.csv (duplicate ID occurrences)
- Caches output to data/cache/league_2026.json
"""

import os
import json
import pandas as pd
import numpy as np
from scipy.stats import percentileofscore
from typing import Dict, Any, Tuple, List, Optional

from pybaseball import statcast, playerid_lookup, playerid_reverse_lookup


def _clean_col(c: str) -> str:
    return (
        c.strip()
         .lstrip("\ufeff")
         .replace("%", "pct")
         .replace(" ", "_")
         .replace("/", "_per_")
         .replace("-", "_")
         .lower()
    )


class LeagueStatcastBuilder:
    def __init__(
        self,
        scoring_path: str,
        fg_hitting_path: str,
        fg_pitching_path: str,
        master_ids_path: str = r"data/ids/master_ids.csv",
        cache_dir: str = "data/cache",
        unmatched_audit_path: str = "data/cache/unmatched_players.csv",
        unmatched_statcast_path: str = "data/cache/unmatched_statcast_players.csv",
        duplicate_mlbam_path: str = "data/cache/duplicate_mlbam_players.csv",
        duplicate_ids_path: str = "data/cache/duplicate_ids.csv",
        season: int = 2026,
    ):
        self.scoring_path = scoring_path
        self.fg_hitting_path = fg_hitting_path
        self.fg_pitching_path = fg_pitching_path
        self.master_ids_path = master_ids_path
        self.cache_dir = cache_dir
        self.unmatched_audit_path = unmatched_audit_path
        self.unmatched_statcast_path = unmatched_statcast_path
        self.duplicate_mlbam_path = duplicate_mlbam_path
        self.duplicate_ids_path = duplicate_ids_path
        self.season = season
        os.makedirs(self.cache_dir, exist_ok=True)

        self.start = f"{season}-03-01"
        self.end = f"{season}-11-30"

        if os.path.exists(self.master_ids_path):
            self.id_df = pd.read_csv(self.master_ids_path, dtype=str).fillna("")
            if "name_first" in self.id_df.columns and "name_last" in self.id_df.columns:
                self.id_df["full_name_norm"] = (
                    self.id_df["name_first"].fillna("") + " " + self.id_df["name_last"].fillna("")
                ).str.strip().str.lower()
            elif "name" in self.id_df.columns:
                self.id_df["full_name_norm"] = self.id_df["name"].fillna("").str.strip().str.lower()
            else:
                self.id_df["full_name_norm"] = ""
        else:
            self.id_df = pd.DataFrame()

    def _cache_path(self) -> str:
        return os.path.join(self.cache_dir, "league_2026.json")

    def _statcast_cache_path(self, mlbam: str) -> str:
        return os.path.join(self.cache_dir, f"statcast_player_{mlbam}.parquet")

    def _load_fantrax_scoring(self) -> pd.DataFrame:
        df = pd.read_csv(self.scoring_path, dtype=str).fillna("")
        df.columns = [c.strip() for c in df.columns]
        df.replace({"IFNA": "", "#N/A": "", "NA": "", "N/A": ""}, inplace=True)
        return df

    def _load_fg_table(self, path: str) -> pd.DataFrame:
        df = pd.read_csv(path, dtype=str).fillna("")
        df.columns = [_clean_col(c) for c in df.columns]
        return df

    def _coerce_numeric(self, df: pd.DataFrame) -> pd.DataFrame:
        for col in df.columns:
            if col in ("name", "team", "playerid", "mlbamid", "player_id"):
                continue
            df[col] = df[col].astype(str).str.replace(",", "").str.replace("—", "").str.strip()
            df[col] = pd.to_numeric(df[col].replace("", np.nan), errors="coerce")
        return df

    def _detect_mlbam_from_row(self, row: pd.Series) -> str:
        candidates = ["key_mlbam", "mlbamid", "mlbam", "KEY_MLBAM", "MLBAMID", "MLBAM"]
        for c in candidates:
            if c in row.index:
                val = str(row.get(c, "")).strip()
                if val:
                    return val
        for c in row.index:
            if "mlbam" in c.lower():
                val = str(row.get(c, "")).strip()
                if val:
                    return val
        return ""

    def _detect_fangraphs_key_from_row(self, row: pd.Series) -> str:
        candidates = ["key_fangraphs", "KEY_FANGRAPHS", "key_fangraphs".lower()]
        for c in candidates:
            if c in row.index:
                val = str(row.get(c, "")).strip()
                if val:
                    return val
        for c in row.index:
            if "fangraph" in c.lower():
                val = str(row.get(c, "")).strip()
                if val:
                    return val
        return ""

    def _resolve_mlbam_for_player(self, p: Dict[str, Any]) -> Optional[str]:
        mlb = p.get("mlbam_id")
        if mlb:
            return str(mlb)

        fg_ids = []
        if p.get("player_id_hitting"):
            fg_ids.append(str(p.get("player_id_hitting")))
        if p.get("player_id_pitching"):
            fg_ids.append(str(p.get("player_id_pitching")))

        for fg_id in fg_ids:
            try:
                df = playerid_reverse_lookup(fg_id, key_type="fangraphs")
                if not df.empty and "key_mlbam" in df.columns:
                    val = df["key_mlbam"].iloc[0]
                    if pd.notna(val):
                        return str(int(val))
            except Exception:
                continue

        name = (p.get("name") or "").strip()
        team = (p.get("team") or "").strip().upper()
        if name:
            parts = name.split()
            if len(parts) >= 2:
                first = parts[0]
                last = " ".join(parts[1:])
            else:
                first = parts[0]
                last = ""
            try:
                df = playerid_lookup(last, first)
                if not df.empty:
                    if team:
                        df_team = df[df["mlb_team"].str.upper() == team]
                        if not df_team.empty:
                            df = df_team
                    df = df.sort_values("mlb_played_last", ascending=False)
                    val = df["key_mlbam"].iloc[0]
                    if pd.notna(val):
                        return str(int(val))
            except Exception:
                pass

        return None

    def _fetch_statcast_for_mlbam(self, mlbam: str) -> Optional[pd.DataFrame]:
        cache = self._statcast_cache_path(mlbam)
        try:
            if os.path.exists(cache):
                return pd.read_parquet(cache)
        except Exception:
            pass

        try:
            df = statcast(self.start, self.end, player_id=int(mlbam))
            if df is None or df.empty:
                return None
            os.makedirs(self.cache_dir, exist_ok=True)
            df.to_parquet(cache, index=False)
            return df
        except Exception:
            return None

    def _compute_hitting_summary_from_statcast(self, df: pd.DataFrame, mlbam: str) -> Dict[str, float]:
        sub = df[df["batter"] == int(mlbam)]
        if sub.empty:
            return {}

        def pct(series, condition):
            total = len(series)
            if total == 0:
                return np.nan
            return 100.0 * (condition(series).sum() / total)

        launch_speed = sub.get("launch_speed", pd.Series([np.nan] * len(sub)))
        barrel = sub.get("barrel", pd.Series([0] * len(sub)))
        bb_type = sub.get("bb_type", pd.Series([None] * len(sub)))
        est_woba = sub.get("estimated_woba_using_speedangle", sub.get("estimated_woba_using_speedangle2", pd.Series([np.nan] * len(sub))))
        est_slg = sub.get("estimated_slg_using_speedangle", sub.get("estimated_slg_using_speedangle2", pd.Series([np.nan] * len(sub))))
        desc = sub.get("description", pd.Series([None] * len(sub)))
        zone = sub.get("zone", pd.Series([np.nan] * len(sub)))
        events = sub.get("events", pd.Series([None] * len(sub)))
        delta_run = sub.get("delta_run_exp", sub.get("delta_run_exp2", pd.Series([0.0] * len(sub))))

        def swing_mask(s):
            return s.isin(["swinging_strike", "swinging_strike_blocked", "foul", "foul_tip"])

        def whiff_mask(s):
            return s.isin(["swinging_strike", "swinging_strike_blocked"])

        def chase_mask(zone_s, desc_s):
            return (zone_s == 0) & swing_mask(desc_s)

        def k_events_mask(ev):
            return ev.isin(["strikeout", "strikeout_double_play"])

        def bb_events_mask(ev):
            return ev.isin(["walk", "hit_by_pitch"])

        swings = swing_mask(desc)
        whiffs = whiff_mask(desc)
        chases = chase_mask(zone, desc)

        total_swings = swings.sum()
        total_whiffs = whiffs.sum()
        total_chases = chases.sum()

        pa_mask = events.notna()
        total_pa = pa_mask.sum()
        k_events = k_events_mask(events)
        bb_events = bb_events_mask(events)

        chase_pct = 100.0 * (total_chases / total_swings) if total_swings > 0 else np.nan
        whiff_pct = 100.0 * (total_whiffs / total_swings) if total_swings > 0 else np.nan
        k_pct = 100.0 * (k_events.sum() / total_pa) if total_pa > 0 else np.nan
        bb_pct = 100.0 * (bb_events.sum() / total_pa) if total_pa > 0 else np.nan

        summary = {
            "avg_ev": float(launch_speed.mean()) if not launch_speed.isna().all() else np.nan,
            "max_ev": float(launch_speed.max()) if not launch_speed.isna().all() else np.nan,
            "hardhit_rate": pct(launch_speed, lambda s: s >= 95),
            "barrel_rate": pct(barrel, lambda s: s == 1),
            "xwoba": float(est_woba.mean()) if not est_woba.isna().all() else np.nan,
            "xslg": float(est_slg.mean()) if not est_slg.isna().all() else np.nan,
            "gb_pct": pct(bb_type, lambda s: s == "ground_ball"),
            "bat_run_value": float(delta_run.sum()),
            "chase_pct": chase_pct,
            "whiff_pct": whiff_pct,
            "k_pct": k_pct,
            "bb_pct": bb_pct,
        }

        return summary

    def _compute_pitching_summary_from_statcast(self, df: pd.DataFrame, mlbam: str) -> Dict[str, float]:
        sub = df[df["pitcher"] == int(mlbam)]
        if sub.empty:
            return {}

        def pct(series, condition):
            total = len(series)
            if total == 0:
                return np.nan
            return 100.0 * (condition(series).sum() / total)

        launch_speed = sub.get("launch_speed", pd.Series([np.nan] * len(sub)))
        barrel = sub.get("barrel", pd.Series([0] * len(sub)))
        bb_type = sub.get("bb_type", pd.Series([None] * len(sub)))
        desc = sub.get("description", pd.Series([None] * len(sub)))
        zone = sub.get("zone", pd.Series([np.nan] * len(sub)))
        events = sub.get("events", pd.Series([None] * len(sub)))
        delta_run = sub.get("delta_run_exp", sub.get("delta_run_exp2", pd.Series([0.0] * len(sub))))

        def swing_mask(s):
            return s.isin(["swinging_strike", "swinging_strike_blocked", "foul", "foul_tip"])

        def whiff_mask(s):
            return s.isin(["swinging_strike", "swinging_strike_blocked"])

        def chase_mask(zone_s, desc_s):
            return (zone_s == 0) & swing_mask(desc_s)

        def k_events_mask(ev):
            return ev.isin(["strikeout", "strikeout_double_play"])

        def bb_events_mask(ev):
            return ev.isin(["walk", "hit_by_pitch"])

        swings = swing_mask(desc)
        whiffs = whiff_mask(desc)
        chases = chase_mask(zone, desc)

        total_swings = swings.sum()
        total_whiffs = whiffs.sum()
        total_chases = chases.sum()

        pa_mask = events.notna()
        total_pa = pa_mask.sum()
        k_events = k_events_mask(events)
        bb_events = bb_events_mask(events)

        chase_pct = 100.0 * (total_chases / total_swings) if total_swings > 0 else np.nan
        whiff_pct = 100.0 * (total_whiffs / total_swings) if total_swings > 0 else np.nan
        k_pct = 100.0 * (k_events.sum() / total_pa) if total_pa > 0 else np.nan
        bb_pct = 100.0 * (bb_events.sum() / total_pa) if total_pa > 0 else np.nan

        summary = {
            "avg_ev_allowed": float(launch_speed.mean()) if not launch_speed.isna().all() else np.nan,
            "max_ev_allowed": float(launch_speed.max()) if not launch_speed.isna().all() else np.nan,
            "hardhit_rate_allowed": pct(launch_speed, lambda s: s >= 95),
            "barrel_rate_allowed": pct(barrel, lambda s: s == 1),
            "gb_pct": pct(bb_type, lambda s: s == "ground_ball"),
            "pitch_run_value": float(-delta_run.sum()),
            "chase_pct": chase_pct,
            "whiff_pct": whiff_pct,
            "k_pct": k_pct,
            "bb_pct": bb_pct,
        }

        return summary

    def _build_unified_players(self, hit_df: pd.DataFrame, pit_df: pd.DataFrame, scoring_df: pd.DataFrame) -> Dict[str, Any]:
        players: Dict[str, Dict] = {}

        scoring_df_cols = [c.strip() for c in scoring_df.columns]
        scoring_df.columns = scoring_df_cols

        fantrax_map_by_mlb: Dict[str, List[Dict[str, Any]]] = {}
        fantrax_map_by_fangraphs: Dict[str, List[Dict[str, Any]]] = {}
        fantrax_map_by_name_team: Dict[tuple, List[Dict[str, Any]]] = {}

        id_counts = {}
        mlbam_counts = {}

        for idx, row in scoring_df.iterrows():
            mlbam = self._detect_mlbam_from_row(row)
            key_fg = self._detect_fangraphs_key_from_row(row)
            name = str(row.get("Player") or row.get("player") or "").strip()
            team = str(row.get("Team") or row.get("team") or "").strip().upper()
            fid = str(row.get("ID") or row.get("Id") or row.get("id") or "").strip()

            meta = {
                "fantrax_id": fid,
                "position": row.get("Position") or row.get("position") or "",
                "player": name,
                "team": team,
                "mlbam": mlbam,
                "key_fangraphs": key_fg,
                "raw_row": row.to_dict(),
                "scoring_index": idx,
            }

            if fid:
                id_counts[fid] = id_counts.get(fid, 0) + 1
            if mlbam:
                mlbam_counts[mlbam] = mlbam_counts.get(mlbam, 0) + 1

            if mlbam:
                fantrax_map_by_mlb.setdefault(mlbam, []).append(meta)
            if key_fg:
                fantrax_map_by_fangraphs.setdefault(key_fg, []).append(meta)
            fantrax_map_by_name_team.setdefault((name.lower(), team), []).append(meta)

        try:
            dup_mlbam = [
                {"mlbam": k, "count": v, "examples": [m.get("player") for m in fantrax_map_by_mlb.get(k, [])]}
                for k, v in mlbam_counts.items()
                if v > 1
            ]
            if dup_mlbam:
                pd.DataFrame(dup_mlbam).to_csv(self.duplicate_mlbam_path, index=False)
        except Exception:
            pass

        try:
            dup_ids = [{"id": k, "count": v} for k, v in id_counts.items() if v > 1]
            if dup_ids:
                pd.DataFrame(dup_ids).to_csv(self.duplicate_ids_path, index=False)
        except Exception:
            pass

        if "mlbamid" in hit_df.columns:
            hit_df["mlbamid"] = hit_df["mlbamid"].astype(str)
        for _, row in hit_df.iterrows():
            mlb = str(row.get("mlbamid", "")).strip()
            pid = str(row.get("playerid", "") or row.get("player_id", "") or "")
            name = str(row.get("name", "")).strip()
            team = str(row.get("team", "")).strip().upper()
            metrics = {}
            for col in hit_df.columns:
                if col in ("name", "team", "playerid", "mlbamid"):
                    continue
                val = row.get(col)
                metrics[col] = None if pd.isna(val) else float(val)
            key = mlb or pid or name
            players.setdefault(
                key,
                {"name": name, "team": team, "mlbam_id": mlb or None, "hitting": {}, "pitching": {}, "fantrax": {}},
            )
            players[key]["hitting"] = metrics
            players[key]["player_id_hitting"] = pid

        if "mlbamid" in pit_df.columns:
            pit_df["mlbamid"] = pit_df["mlbamid"].astype(str)
        for _, row in pit_df.iterrows():
            mlb = str(row.get("mlbamid", "")).strip()
            pid = str(row.get("playerid", "") or row.get("player_id", "") or "")
            name = str(row.get("name", "")).strip()
            team = str(row.get("team", "")).strip().upper()
            metrics = {}
            for col in pit_df.columns:
                if col in ("name", "team", "playerid", "mlbamid"):
                    continue
                val = row.get(col)
                metrics[col] = None if pd.isna(val) else float(val)
            key = mlb or pid or name
            players.setdefault(
                key,
                {"name": name, "team": team, "mlbam_id": mlb or None, "hitting": {}, "pitching": {}, "fantrax": {}},
            )
            players[key]["pitching"] = metrics
            players[key]["player_id_pitching"] = pid

        unmatched_rows = []
        for idx, row in scoring_df.iterrows():
            mlbam = self._detect_mlbam_from_row(row)
            key_fg = self._detect_fangraphs_key_from_row(row)
            name = str(row.get("Player") or row.get("player") or "").strip()
            team = str(row.get("Team") or row.get("team") or "").strip().upper()
            fid = str(row.get("ID") or row.get("Id") or row.get("id") or "").strip()

            mapped_keys: List[str] = []

            if mlbam:
                for k, p in players.items():
                    if p.get("mlbam_id") and str(p.get("mlbam_id")) == mlbam:
                        mapped_keys.append(k)
                if mlbam in players:
                    mapped_keys.append(mlbam)

            if not mapped_keys and key_fg:
                for k, p in players.items():
                    if p.get("player_id_hitting") and str(p.get("player_id_hitting")) == key_fg:
                        mapped_keys.append(k)
                    if p.get("player_id_pitching") and str(p.get("player_id_pitching")) == key_fg:
                        mapped_keys.append(k)

            if not mapped_keys:
                for k, p in players.items():
                    if p.get("name", "").strip().lower() == name.lower() and p.get("team", "").strip().upper() == team:
                        mapped_keys.append(k)

            mapped_keys = list(dict.fromkeys(mapped_keys))

            if mapped_keys:
                for mapped_key in mapped_keys:
                    meta = {
                        "fantrax_id": fid,
                        "position": row.get("Position") or row.get("position") or "",
                        "player": name,
                        "team": team,
                        "mlbam": mlbam,
                        "key_fangraphs": key_fg,
                        "scoring_index": idx,
                    }
                    existing = players[mapped_key].get("fantrax", {}) or {}
                    if not existing:
                        players[mapped_key]["fantrax"] = meta
                    else:
                        merged = existing.copy()
                        for k2, v2 in meta.items():
                            if not merged.get(k2) and v2:
                                merged[k2] = v2
                        players[mapped_key]["fantrax"] = merged
                    if meta.get("position"):
                        players[mapped_key]["position"] = meta.get("position")
            else:
                unmatched_rows.append(row.to_dict())

        for k, p in players.items():
            p.setdefault("fantrax", {})
            p.setdefault("position", p.get("position") or None)

        if unmatched_rows:
            try:
                unmatched_df = pd.DataFrame(unmatched_rows)
                os.makedirs(os.path.dirname(self.unmatched_audit_path), exist_ok=True)
                unmatched_df.to_csv(self.unmatched_audit_path, index=False)
            except Exception:
                pass

        unmatched_statcast_players = []

        for key, p in players.items():
            mlbam = self._resolve_mlbam_for_player(p)
            if not mlbam:
                unmatched_statcast_players.append(
                    {
                        "key": key,
                        "name": p.get("name"),
                        "team": p.get("team"),
                        "player_id_hitting": p.get("player_id_hitting"),
                        "player_id_pitching": p.get("player_id_pitching"),
                    }
                )
                continue

            p["mlbam_id"] = mlbam

            df_sc = self._fetch_statcast_for_mlbam(mlbam)
            if df_sc is None or df_sc.empty:
                unmatched_statcast_players.append(
                    {
                        "key": key,
                        "name": p.get("name"),
                        "team": p.get("team"),
                        "mlbam_id": mlbam,
                        "reason": "no_statcast_rows",
                    }
                )
                continue

            hit_summary = self._compute_hitting_summary_from_statcast(df_sc, mlbam)
            pit_summary = self._compute_pitching_summary_from_statcast(df_sc, mlbam)

            if hit_summary:
                p.setdefault("hitting", {})
                for col, val in hit_summary.items():
                    if val is not None and not (isinstance(val, float) and np.isnan(val)):
                        p["hitting"][col] = float(val)

            if pit_summary:
                p.setdefault("pitching", {})
                for col, val in pit_summary.items():
                    if val is not None and not (isinstance(val, float) and np.isnan(val)):
                        p["pitching"][col] = float(val)

        if unmatched_statcast_players:
            try:
                df_un = pd.DataFrame(unmatched_statcast_players)
                os.makedirs(os.path.dirname(self.unmatched_statcast_path), exist_ok=True)
                df_un.to_csv(self.unmatched_statcast_path, index=False)
            except Exception:
                pass

        return players

    def _compute_percentiles_for_group(self, players: Dict[str, Dict], side: str):
        metric_names = set()
        for p in players.values():
            metrics = p.get(side, {})
            metric_names.update([k for k, v in metrics.items() if v is not None])

        dists = {}
        for m in metric_names:
            vals = [p.get(side, {}).get(m) for p in players.values() if p.get(side, {}).get(m) is not None]
            if vals:
                dists[m] = vals

        for key, p in players.items():
            p.setdefault("percentiles", {})
            side_metrics = p.get(side, {})
            for m in metric_names:
                v = side_metrics.get(m)
                if v is None or m not in dists or not dists[m]:
                    pct = None
                else:
                    try:
                        pct = float(percentileofscore(dists[m], v))
                    except Exception:
                        pct = None
                p["percentiles"].setdefault(side, {})[m] = pct

    def build_league(self) -> Dict[str, Any]:
        cache = self._cache_path()
        if os.path.exists(cache):
            try:
                with open(cache, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                try:
                    os.remove(cache)
                except Exception:
                    pass

        scoring_df = self._load_fantrax_scoring()
        hit_df = self._load_fg_table(self.fg_hitting_path)
        pit_df = self._load_fg_table(self.fg_pitching_path)

        hit_df = self._coerce_numeric(hit_df)
        pit_df = self._coerce_numeric(pit_df)

        players = self._build_unified_players(hit_df, pit_df, scoring_df)

        self._compute_percentiles_for_group(players, "hitting")
        self._compute_percentiles_for_group(players, "pitching")

        league = {"season": str(self.season), "players": players}

        try:
            with open(cache, "w", encoding="utf-8") as f:
                json.dump(league, f, indent=2, default=str)
        except Exception:
            pass

        return league
