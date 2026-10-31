"""Shared helpers for reading the FlyRank warehouse release and building the Lane 2 frame.

Files are fetched once with huggingface_hub and cached locally, so a notebook re-run does
not hit Hugging Face again. If FLYRANK_WAREHOUSE_DIR points at a local copy of the release
(same folder layout as the Hub repo), that copy is used instead.

The token is read from the HF_TOKEN environment variable, a Colab secret named HF_TOKEN, or
an existing `hf auth login`. It is never printed.
"""

import os
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

REPO_ID = "FlyRank/internship-warehouse"


def _token():
    if os.environ.get("HF_TOKEN"):
        return os.environ["HF_TOKEN"]
    try:
        from google.colab import userdata  # type: ignore

        return userdata.get("HF_TOKEN")
    except Exception:
        pass
    from huggingface_hub import get_token

    return get_token()


def file_path(rel: str) -> str:
    """Local path for a file in the release, downloading it on first use."""
    mirror = os.environ.get("FLYRANK_WAREHOUSE_DIR")
    if mirror and (Path(mirror) / rel).exists():
        return (Path(mirror) / rel).as_posix()
    from huggingface_hub import hf_hub_download

    return Path(hf_hub_download(REPO_ID, rel, repo_type="dataset", token=_token())).as_posix()


def month_path(month: str) -> str:
    """Path to one monthly partition of the daily fact table, e.g. month_path('2026-03')."""
    return file_path(f"fact_content_daily_performance/month={month}/data_0.parquet")


def connect() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    con.execute("SET threads TO 4")
    return con


# --------------------------------------------------------------------------------------
# Lane 2 frame: one row per page at a decision date t (first day of the label month).
# Features come only from the feature month (the calendar month before t).
# The label comes only from the label month (the calendar month starting at t).
# --------------------------------------------------------------------------------------

FEATURE_SQL = """
SELECT
    client_hash_id,
    content_hash_id,
    SUM(gsc_impressions)                                                AS imp,
    SUM(gsc_clicks)                                                     AS clicks,
    COUNT(DISTINCT report_date) FILTER (WHERE gsc_impressions > 0)      AS days_visible,
    SUM(gsc_avg_position * gsc_impressions) / NULLIF(SUM(gsc_impressions), 0)
                                                                        AS avg_position,
    SUM(gsc_impressions) FILTER (WHERE day(report_date) <= 15) / 15.0   AS imp_per_day_h1,
    SUM(gsc_impressions) FILTER (WHERE day(report_date) > 15) / ({days} - 15.0)
                                                                        AS imp_per_day_h2
FROM read_parquet('{path}')
WHERE gsc_data_available IS TRUE
GROUP BY 1, 2
"""

LABEL_SQL = """
SELECT content_hash_id, SUM(gsc_impressions) AS imp_next
FROM read_parquet('{path}')
WHERE gsc_data_available IS TRUE
GROUP BY 1
"""

# Search Console rows only exist on days a page earned impressions, so tracking coverage
# has to be checked per client: a client counts as tracked in a month when its pages have
# GSC rows on every calendar day of that month.
COVERAGE_SQL = """
SELECT client_hash_id, COUNT(DISTINCT report_date) AS gsc_days
FROM read_parquet('{path}')
WHERE gsc_data_available IS TRUE
GROUP BY 1
"""

MIN_IMPRESSIONS = 100   # volume floor on the feature month
DECLINE_CUT = -20.0     # page change worse than -20% ...
CLIENT_MARGIN = -20.0   # ... and at least 20 points worse than its client's median change


def days_in(month: str) -> int:
    return pd.Period(month).days_in_month


def tracked_clients(con, month: str) -> set:
    cov = con.sql(COVERAGE_SQL.format(path=month_path(month))).df()
    return set(cov.loc[cov["gsc_days"].eq(days_in(month)), "client_hash_id"])


def build_frame(con, feature_month: str, label_month: str) -> pd.DataFrame:
    """Eligible pages with the contract features, a few extras, and the client-relative label."""
    d_now, d_next = days_in(feature_month), days_in(label_month)
    feats = con.sql(FEATURE_SQL.format(path=month_path(feature_month), days=d_now)).df()
    labels = con.sql(LABEL_SQL.format(path=month_path(label_month))).df()
    content = con.sql(
        f"SELECT content_hash_id, content_created_date, word_count "
        f"FROM read_parquet('{file_path('dim_content.parquet')}')"
    ).df()
    tracked = tracked_clients(con, feature_month) & tracked_clients(con, label_month)

    t = pd.Timestamp(f"{label_month}-01")
    df = feats.merge(labels, on="content_hash_id", how="left").merge(content, on="content_hash_id", how="left")
    # A page with no GSC rows next month, at a client that was tracked all month, earned zero impressions.
    df["imp_next"] = df["imp_next"].fillna(0)

    df = df[
        df["client_hash_id"].isin(tracked)
        & df["imp"].ge(MIN_IMPRESSIONS)
        & pd.to_datetime(df["content_created_date"]).lt(t - pd.Timedelta(days=30))
    ].copy()

    # The five contract features (feature month or fixed metadata only).
    df["log_imp"] = np.log1p(df["imp"])
    df["momentum"] = np.log1p(df["imp_per_day_h2"].fillna(0)) - np.log1p(df["imp_per_day_h1"].fillna(0))
    df["content_age_days"] = (t - pd.to_datetime(df["content_created_date"])).dt.days

    # Extras used from week 4 on.
    df["ctr_pct"] = df["clicks"] / df["imp"] * 100
    df["log_clicks"] = np.log1p(df["clicks"])

    # Label: per-day impressions next month vs this month, relative to the page's own client.
    per_day_now = df["imp"] / d_now
    per_day_next = df["imp_next"] / d_next
    df["change_pct"] = (per_day_next - per_day_now) / per_day_now * 100
    df["client_median_change"] = df.groupby("client_hash_id")["change_pct"].transform("median")
    df["vs_client"] = df["change_pct"] - df["client_median_change"]
    df["label"] = (df["change_pct"].lt(DECLINE_CUT) & df["vs_client"].lt(CLIENT_MARGIN)).astype(int)

    # Demand at stake if the page declines (used for demand captured@K).
    df["lost_per_day"] = (per_day_now - per_day_next).clip(lower=0)

    df["feature_month"] = feature_month
    df["label_month"] = label_month
    # Fixed row order, so seeded randomness and tie-breaks reproduce run to run.
    return df.sort_values("content_hash_id").reset_index(drop=True)


FIVE_FEATURES = ["log_imp", "days_visible", "avg_position", "momentum", "content_age_days"]


def precision_at_k(score, y, k=50):
    order = np.argsort(-np.asarray(score, dtype=float), kind="stable")
    return float(np.asarray(y)[order[:k]].mean())


def demand_captured_at_k(score, y, lost, k=50):
    y, lost = np.asarray(y), np.asarray(lost, dtype=float)
    order = np.argsort(-np.asarray(score, dtype=float), kind="stable")
    found = (lost[order[:k]] * y[order[:k]]).sum()
    best = np.sort(lost * y)[::-1][:k].sum()
    return float(found / best) if best > 0 else float("nan")
