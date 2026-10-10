"""Retrospective time-aware backtest, with June values unavailable until model freeze.

Stages: plan, self-check, inspect, develop, aggregate, freeze, evaluate.
No token argument, raw exports, current snapshot metadata, or query-table features.
The prepared script is not evidence that gated warehouse queries have executed.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
from urllib.parse import urlparse
from datetime import datetime, timezone

import duckdb
import joblib
import numpy as np
import pandas as pd
from huggingface_hub import HfApi, get_token
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from capstone_analysis import metrics as starter_metrics

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "work/outputs"
CACHE = OUT / "warehouse_cache"
EXTENSION = ROOT / "work/capstones/ML_Google_Search_Ranking_and_Discoverability"
REPO = "FlyRank/internship-warehouse"
REVISION = "50cbf7c3909d07be4d1b5906b4d09e882e5acbf2"
BASE = f"hf://datasets/{REPO}@{REVISION}"
SEED = 2030
RUN_TYPE = "original fixed-holdout retrospective backtest"
TEST_DATE = pd.Timestamp("2026-06-01")
DECISIONS = ["2025-12-01", "2026-02-01", "2026-04-01", "2026-06-01"]
TRAIN_DATES = DECISIONS[:2]
VALIDATION_DATE = DECISIONS[2]
DAILY_REQUIRED = {"report_date", "client_hash_id", "content_hash_id", "gsc_impressions", "gsc_clicks",
                  "gsc_avg_position", "gsc_data_available"}
CLIENT_REQUIRED = {"client_hash_id", "gsc_data_start"}
FEATURES = ["log_impressions90", "log_clicks90", "log_impressions30", "ctr90_pct", "position90",
            "position30", "position_variation90", "prior_momentum_pct", "coverage90", "coverage30",
            "has_position", "has_complete_clicks90", "active_impression_days90", "days_since_last_impression"]
POLICY = {
    "source_repository": REPO, "revision": REVISION,
    "release_build": "flyrank_pseudonymized_warehouse_release_v20260703",
    "decisions_at_midnight": DECISIONS, "training_decisions": TRAIN_DATES,
    "validation_decision": VALIDATION_DATE, "test_decision": "2026-06-01",
    "feature_window": "[D-90 days,D)", "prior_reference": "[D-30 days,D)",
    "past_comparison": "[D-60 days,D-30 days)", "outcome": "[D,D+30 days)",
    "minimum_observed_feature_days": 72, "minimum_observed_reference_days": 24,
    "minimum_observed_past_comparison_days": 24, "minimum_prior_impressions": 100,
    "minimum_observed_outcome_days": 24, "decline_rate_ratio_threshold": .8,
    "client_start_required_before_feature_start": True,
    "observed_search_rule": "gsc_data_available IS TRUE and non-null, finite nonnegative impressions; invalid metrics counted and excluded",
    "position_rule": "only finite positive measured positions; impression-weighted aggregation; do not use position zero as rank",
    "target_rule": "future observed daily impression rate / prior observed daily impression rate < 0.8",
    "no_positive_future_volume_filter": True, "feature_columns": FEATURES,
    "client_test_fraction": .25, "client_validation_fraction_of_remaining": .25,
    "seed": SEED, "maximum_fit_rows": 250000,
    "model_selection": "highest validation average precision, fixed two candidates; never June outcomes",
    "baseline": "new prior-only rule: 65% prior decline momentum, 20% train-CDF visibility, 15% measured-position opportunity",
    "candidates": {"logistic_regression": {"C": 1., "max_iter": 1500},
                   "random_forest": {"n_estimators": 120, "max_depth": 8, "min_samples_leaf": 50}},
    "no_snapshot_or_query_features": True,
    "availability_limitation": "report dates are historical but ingestion/as-of vintages are unavailable; finalized snapshot backtest, not prospective live collection",
}


class SafeFailure(RuntimeError):
    """A diagnostic whose message contains no credential or identifying row."""


def metrics(y, score):
    result=starter_metrics(y,score)
    if not result["both_classes_observed"]:
        result["average_precision"]=None
        result["discrimination_note"]="single observed class; discrimination undefined, precision descriptive only"
    return result


def dump(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=str, allow_nan=False), encoding="utf-8")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def contract_hash():
    return hashlib.sha256(json.dumps(POLICY, sort_keys=True).encode()).hexdigest()


def prepare_cache():
    CACHE.mkdir(parents=True, exist_ok=True)
    (CACHE / ".gitignore").write_text("*\n!.gitignore\n", encoding="utf-8")
    return CACHE


def token_available():
    return bool(get_token())


def connect(remote=False):
    prepare_cache()
    con = duckdb.connect()
    con.execute("SET threads=4")
    con.execute("SET memory_limit='3GB'")
    con.execute("SET enable_progress_bar=false")
    con.execute("SET temp_directory=?", [str(CACHE / "duckdb_temp")])
    if remote:
        token = get_token()
        if not token:
            raise SafeFailure("HF authentication is not available. Sign in locally and accept the dataset gate; no warehouse query was run.")
        try:
            con.execute("INSTALL httpfs")
            con.execute("LOAD httpfs")
            # In-memory secret only. Never print this statement or its original exception.
            con.execute("CREATE OR REPLACE SECRET flyrank_read (TYPE huggingface, TOKEN '" + token.replace("'", "''") + "')")
        except Exception:
            raise SafeFailure("DuckDB remote authentication setup failed. Check httpfs/network and local HF access; credential details suppressed.") from None
        finally:
            del token
    return con


def paths_for_months(months):
    info = HfApi(token=False).dataset_info(REPO, revision=REVISION)
    result = [f"{BASE}/{item.rfilename}" for item in info.siblings
              if item.rfilename.startswith("fact_content_daily_performance/month=")
              and item.rfilename.endswith(".parquet")
              and item.rfilename.split("month=", 1)[1].split("/", 1)[0] in months]
    if not result:
        raise SafeFailure("No published daily partitions match the requested months at the pinned revision.")
    return sorted(result)


def relation(paths):
    literals = ",".join("'" + path.replace("'", "''") + "'" for path in paths)
    return f"read_parquet([{literals}], hive_partitioning=true)"


def remote_query(con, sql):
    try:
        return con.sql(sql)
    except Exception as exc:
        kind = type(exc).__name__
        raise SafeFailure(f"Remote query failed ({kind}); details suppressed to protect credentials and rows. Check access, schema, network or rate limits; do not retry June during development.") from None


def schema(con, src):
    rows = remote_query(con, f"DESCRIBE SELECT * FROM {src}").fetchall()
    return {row[0]: row[1] for row in rows}


def input_audit(con, src):
    result = remote_query(con, f"""SELECT COUNT(*),MIN(report_date),MAX(report_date),
      COUNT(*) FILTER (WHERE report_date IS NULL OR client_hash_id IS NULL OR content_hash_id IS NULL),
      COUNT(*) FILTER (WHERE gsc_data_available IS TRUE AND
        (gsc_impressions IS NULL OR gsc_impressions<0 OR NOT isfinite(gsc_impressions))),
      COUNT(*) FILTER (WHERE gsc_data_available IS TRUE AND
        (gsc_clicks IS NULL OR gsc_clicks<0 OR NOT isfinite(gsc_clicks)))
      FROM {src}""").fetchone()
    if result[3]:
        raise SafeFailure("Actual daily data contains null dates or join keys; stop rather than silently combine unidentified observations.")
    return result


def inspect():
    con = connect(remote=True)
    march = relation(paths_for_months({"2026-03"}))
    clients = f"read_parquet('{BASE}/dim_clients.parquet')"
    daily_schema, client_schema = schema(con, march), schema(con, clients)
    missing = {"daily": sorted(DAILY_REQUIRED-set(daily_schema)), "clients": sorted(CLIENT_REQUIRED-set(client_schema))}
    receipt = {"stage": "inspect", "status": "schema inspected", "revision": REVISION,
               "daily_schema": daily_schema, "client_schema": client_schema, "missing_required": missing}
    dump(OUT / "warehouse_schema_audit.json", receipt)
    if any(missing.values()):
        raise SafeFailure("Verified warehouse schema does not satisfy the predeclared contract; inspect warehouse_schema_audit.json before changing any assumptions.")
    stats = input_audit(con, march)
    duplicates = remote_query(con, f"SELECT COUNT(*) FROM (SELECT report_date,client_hash_id,content_hash_id FROM {march} GROUP BY 1,2,3 HAVING COUNT(*)>1)").fetchone()[0]
    dim_stats = remote_query(con, f"SELECT COUNT(*), COUNT(DISTINCT client_hash_id), COUNT(*) FILTER (WHERE client_hash_id IS NULL), COUNT(*) FILTER (WHERE gsc_data_start IS NULL) FROM {clients}").fetchone()
    if duplicates or dim_stats[0] != dim_stats[1] or dim_stats[2]:
        raise SafeFailure("Actual grain/dimension cardinality audit failed; no model may be fitted.")
    if dim_stats[0] != 104:
        raise SafeFailure("Actual client dimension count differs from the documented release; review the pinned dataset before modeling.")
    client_frame = remote_query(con, f"SELECT client_hash_id,gsc_data_start FROM {clients}").df()
    local = connect()
    local.register("clients", client_frame)
    local.execute("COPY clients TO ? (FORMAT PARQUET)", [str(CACHE / "clients.parquet")])
    receipt.update({"status": "passed", "march_rows": int(stats[0]), "march_min_date": str(stats[1]),
                    "march_max_date": str(stats[2]), "march_duplicate_grains": int(duplicates),
                    "client_rows": int(dim_stats[0]), "clients_with_unknown_gsc_start": int(dim_stats[3]),
                    "march_null_dates_or_keys": int(stats[3]), "march_unusable_impression_metrics": int(stats[4]),
                    "march_unusable_click_metrics": int(stats[5]),
                    "client_join_one_to_one": True, "june_values_accessed": False})
    receipt["clients_cache_sha256"]=digest(CACHE/"clients.parquet")
    receipt["source_code_sha256"]=digest(Path(__file__))
    dump(OUT / "warehouse_schema_audit.json", receipt)
    print(json.dumps({key:value for key,value in receipt.items() if key not in {"daily_schema","client_schema"}}, indent=2))
    return receipt


def aggregation_sql(src, decisions):
    """All input is past-May; June target clauses are disabled, even in mixed windows."""
    bounds = ",".join(f"(DATE '{date}')" for date in decisions)
    earliest = min(pd.Timestamp(date) for date in decisions)-pd.Timedelta(days=90)
    last_decision=max(pd.Timestamp(date) for date in decisions)
    latest=min(last_decision+pd.Timedelta(days=30),TEST_DATE)
    pre = "report_date >= d-INTERVAL 90 DAY AND report_date < d"
    ref = "report_date >= d-INTERVAL 30 DAY AND report_date < d"
    old = "report_date >= d-INTERVAL 60 DAY AND report_date < d-INTERVAL 30 DAY"
    future = "d < DATE '2026-06-01' AND report_date >= d AND report_date < d+INTERVAL 30 DAY"
    valid = "gsc_data_available IS TRUE AND gsc_impressions IS NOT NULL AND gsc_impressions >= 0 AND isfinite(gsc_impressions)"
    return f"""
    WITH daily AS (
      SELECT CAST(report_date AS DATE) report_date,client_hash_id,content_hash_id,COUNT(*) grain_rows,
             ANY_VALUE(gsc_data_available) gsc_data_available,ANY_VALUE(gsc_impressions) gsc_impressions,
             ANY_VALUE(gsc_clicks) gsc_clicks,ANY_VALUE(gsc_avg_position) gsc_avg_position
      FROM {src} WHERE report_date >= DATE '{earliest.date()}' AND report_date < DATE '{latest.date()}'
      GROUP BY 1,2,3
    ), bounds(d) AS (VALUES {bounds}), joined AS (
      SELECT *,({valid}) AS observed_search FROM daily CROSS JOIN bounds
      WHERE report_date >= d-INTERVAL 90 DAY
        AND report_date < CASE WHEN d < DATE '2026-06-01' THEN d+INTERVAL 30 DAY ELSE d END
    )
    SELECT d decision_date,client_hash_id,content_hash_id,
      SUM(grain_rows-1) duplicate_grain_excess,
      COUNT(*) FILTER (WHERE observed_search AND {pre}) observed90,
      COUNT(*) FILTER (WHERE observed_search AND {ref}) observed30,
      COUNT(*) FILTER (WHERE observed_search AND {old}) observed_old30,
      COUNT(*) FILTER (WHERE observed_search AND {future}) observed_future,
      SUM(gsc_impressions) FILTER (WHERE observed_search AND {pre}) impressions90,
      SUM(gsc_impressions) FILTER (WHERE observed_search AND {ref}) impressions30,
      SUM(gsc_impressions) FILTER (WHERE observed_search AND {old}) impressions_old30,
      SUM(gsc_impressions) FILTER (WHERE observed_search AND {future}) impressions_future,
      SUM(gsc_clicks) FILTER (WHERE observed_search AND gsc_clicks IS NOT NULL AND gsc_clicks >=0 AND isfinite(gsc_clicks) AND {pre}) clicks90,
      COUNT(*) FILTER (WHERE observed_search AND gsc_clicks IS NOT NULL AND gsc_clicks >=0 AND isfinite(gsc_clicks) AND {pre}) clicks_observed90,
      SUM(gsc_impressions*gsc_avg_position) FILTER (WHERE observed_search AND gsc_avg_position>0 AND isfinite(gsc_avg_position) AND {pre}) position_numerator90,
      SUM(gsc_impressions*gsc_avg_position*gsc_avg_position) FILTER (WHERE observed_search AND gsc_avg_position>0 AND isfinite(gsc_avg_position) AND {pre}) position_square90,
      SUM(gsc_impressions) FILTER (WHERE observed_search AND gsc_avg_position>0 AND isfinite(gsc_avg_position) AND {pre}) position_denominator90,
      SUM(gsc_impressions*gsc_avg_position) FILTER (WHERE observed_search AND gsc_avg_position>0 AND isfinite(gsc_avg_position) AND {ref}) position_numerator30,
      SUM(gsc_impressions) FILTER (WHERE observed_search AND gsc_avg_position>0 AND isfinite(gsc_avg_position) AND {ref}) position_denominator30,
      COUNT(*) FILTER (WHERE observed_search AND gsc_impressions>0 AND {pre}) active_impression_days90,
      MAX(report_date) FILTER (WHERE observed_search AND gsc_impressions>0 AND {pre}) last_impression_date
    FROM joined GROUP BY 1,2,3
    """


def require_receipt(name):
    path = OUT / name
    if not path.exists():
        raise SafeFailure(f"Required preceding execution receipt is missing: {name}.")
    result = json.loads(path.read_text(encoding="utf-8"))
    if result.get("status") != "passed" or result.get("revision") != REVISION:
        raise SafeFailure("Preceding execution receipt is not passed for the pinned revision.")
    return result


def cached_query(sql, path, remote=True):
    if path.exists():
        raise SafeFailure("Aggregate cache already exists; use it rather than repeat a remote scan. Changes require explicit researcher review.")
    con = connect(remote=remote)
    try:
        con.execute(f"COPY ({sql}) TO ? (FORMAT PARQUET, COMPRESSION ZSTD)", [str(path)])
    except Exception:
        raise SafeFailure("Aggregate query did not complete; credential/row details suppressed. A cache is not evidence until its receipt passes.") from None
    check = connect()
    result = check.execute("SELECT COUNT(*),COALESCE(SUM(duplicate_grain_excess),0) FROM read_parquet(?)", [str(path)]).fetchone()
    if result[1]:
        raise SafeFailure("Daily grain duplicates were found within study windows; cached aggregation must not be modeled.")
    return int(result[0])


def develop():
    require_receipt("warehouse_schema_audit.json")
    sql = aggregation_sql(relation(paths_for_months({"2026-03"})), ["2026-04-01"])
    rows = cached_query(sql, CACHE / "march_development.parquet")
    receipt = {"stage":"develop", "status":"passed", "revision":REVISION, "aggregate_rows":rows,
               "query_sha256":hashlib.sha256(sql.encode()).hexdigest(), "scope":"March query mechanics only; no model/outcome claims",
               "june_values_accessed":False, "duplicate_grain_excess":0}
    receipt["cache_sha256"]=digest(CACHE/"march_development.parquet")
    receipt["source_code_sha256"]=digest(Path(__file__))
    dump(OUT / "warehouse_development_receipt.json", receipt)
    print(json.dumps(receipt, indent=2)); return receipt


def aggregate():
    require_receipt("warehouse_development_receipt.json")
    months = {str(date)[:7] for date in pd.date_range("2025-01-01", "2026-05-01", freq="MS")}
    src = relation(paths_for_months(months))
    sql = aggregation_sql(src, DECISIONS)
    con = connect(remote=True)
    counts = input_audit(con, src)
    rows = cached_query(sql, CACHE / "development_windows.parquet")
    receipt = {"stage":"aggregate", "status":"passed", "revision":REVISION, "aggregate_rows":rows,
               "development_fact_rows":int(counts[0]), "development_min_date":str(counts[1]),
               "development_max_date":str(counts[2]), "query_sha256":hashlib.sha256(sql.encode()).hexdigest(),
               "null_dates_or_keys":int(counts[3]), "unusable_impression_metrics":int(counts[4]),
               "unusable_click_metrics":int(counts[5]),
               "cache_sha256":digest(CACHE/"development_windows.parquet"), "june_values_accessed":False,
               "scope":"all non-June release partitions; daily grain checked within exact study windows"}
    receipt["source_code_sha256"]=digest(Path(__file__))
    dump(OUT / "warehouse_aggregation_receipt.json", receipt)
    print(json.dumps(receipt, indent=2)); return receipt


def frame_from_cache():
    con = connect()
    frame = con.execute("SELECT a.*,c.gsc_data_start,c.client_hash_id IS NOT NULL AS client_join_matched FROM read_parquet(?) a LEFT JOIN read_parquet(?) c USING(client_hash_id)",
                        [str(CACHE/"development_windows.parquet"),str(CACHE/"clients.parquet")]).df()
    before_count=con.execute("SELECT COUNT(*) FROM read_parquet(?)",[str(CACHE/"development_windows.parquet")]).fetchone()[0]
    if len(frame)!=before_count:
        raise SafeFailure("Client dimension join changed page-at-decision row count; stop before fitting.")
    for field in ["decision_date","last_impression_date","gsc_data_start"]:
        frame[field] = pd.to_datetime(frame[field])
    frame = frame.sort_values(["decision_date","client_hash_id","content_hash_id"],kind="stable").reset_index(drop=True)
    if frame.duplicated(["decision_date","client_hash_id","content_hash_id"]).any():
        raise SafeFailure("Page-at-decision uniqueness failed after the verified client join.")
    history = frame.gsc_data_start.le(frame.decision_date-pd.Timedelta(days=90))
    preeligible = history & frame.observed90.ge(72) & frame.observed30.ge(24) & frame.observed_old30.ge(24) & frame.impressions30.ge(100)
    frame["preeligible"] = preeligible
    frame["prior_rate"] = frame.impressions30/frame.observed30.replace(0,np.nan)
    frame["preeligible"] &= np.isfinite(frame.prior_rate)&frame.prior_rate.gt(0)&np.isfinite(frame.impressions90)
    old_rate = frame.impressions_old30/frame.observed_old30.replace(0,np.nan)
    frame["prior_momentum_pct"] = 100*(frame.prior_rate/old_rate.replace(0,np.nan)-1)
    for window in [90,30]:
        frame[f"position{window}"] = frame[f"position_numerator{window}"]/frame[f"position_denominator{window}"].replace(0,np.nan)
        frame[f"coverage{window}"] = frame[f"observed{window}"]/window
    variance = frame.position_square90/frame.position_denominator90.replace(0,np.nan)-frame.position90**2
    frame["position_variation90"] = np.sqrt(variance.clip(lower=0))
    # Do not mix clicks with a denominator covering days where clicks were missing.
    frame["ctr90_pct"] = (100*frame.clicks90/frame.impressions90).where(frame.clicks_observed90.eq(frame.observed90))
    frame["has_complete_clicks90"] = frame.clicks_observed90.eq(frame.observed90).astype(int)
    frame["has_position"] = frame.position90.notna().astype(int)
    frame["days_since_last_impression"] = (frame.decision_date-frame.last_impression_date).dt.days
    for dest,source in [("log_impressions90","impressions90"),("log_clicks90","clicks90"),("log_impressions30","impressions30")]:
        frame[dest] = np.log1p(frame[source].clip(lower=0))
    frame["log_clicks90"] = frame.log_clicks90.where(frame.has_complete_clicks90.eq(1))
    future_rate = frame.impressions_future/frame.observed_future.replace(0,np.nan)
    frame["label_defined"] = frame.preeligible & frame.observed_future.ge(24) & np.isfinite(future_rate) & future_rate.ge(0)
    ratio = future_rate/frame.prior_rate
    frame["label"] = (ratio < .8).astype(int).where(frame.label_defined)
    frame[FEATURES] = frame[FEATURES].replace([np.inf,-np.inf],np.nan)
    frame.attrs["client_join_audit"] = {"before_rows":int(before_count),"after_rows":len(frame),
                                         "unmatched_rows":int((~frame.client_join_matched).sum()),"unmatched_rows_excluded":True}
    return frame


class PriorRule:
    def fit(self, frame):
        self.visibility = np.sort(frame.log_impressions30.to_numpy()); return self

    def score(self, frame):
        visibility = np.searchsorted(self.visibility,frame.log_impressions30.to_numpy(),side="right")/len(self.visibility)
        momentum = frame.prior_momentum_pct.fillna(0).clip(-100,100).to_numpy()
        position = frame.position30.fillna(50).clip(1,50).to_numpy()
        return .65*(1-momentum/100)/2+.20*visibility+.15*visibility*(50-position)/49


def pipeline(name):
    estimator = (LogisticRegression(C=1.,max_iter=1500,random_state=SEED) if name=="logistic_regression" else
                 RandomForestClassifier(n_estimators=120,max_depth=8,min_samples_leaf=50,n_jobs=4,random_state=SEED))
    steps = [("impute",SimpleImputer(strategy="median"))]
    if name=="logistic_regression": steps.append(("scale",StandardScaler()))
    return Pipeline(steps+[("model",estimator)])


def fitting_sample(frame):
    sample = frame.sample(n=250000,random_state=SEED) if len(frame)>250000 else frame
    if sample.label.nunique()!=2:
        raise SafeFailure("The predetermined fitting sample lacks both observed classes; no fitted model is valid.")
    return sample


def cohort_flow(frame):
    result=[]
    for date,group in frame.groupby("decision_date",sort=True):
        late=group.gsc_data_start.isna()|group.gsc_data_start.gt(group.decision_date-pd.Timedelta(days=90))
        result.append({"decision_date":str(date.date()),"aggregate_page_rows":len(group),"preeligible_rows":int(group.preeligible.sum()),
                       "client_join_unmatched_rows":int((~group.client_join_matched).sum()),
                       "unknown_or_late_search_start":int(late.sum()),"insufficient_90_day_coverage":int(group.observed90.lt(72).sum()),
                       "insufficient_reference_coverage":int(group.observed30.lt(24).sum()),
                       "insufficient_past_comparison_coverage":int(group.observed_old30.lt(24).sum()),
                       "insufficient_prior_impressions":int((group.impressions30.isna()|group.impressions30.lt(100)).sum()),
                       "invalid_prior_rate":int((~np.isfinite(group.prior_rate)|group.prior_rate.le(0)).sum()),
                       "prior_eligible_labels_undefined":(None if date==TEST_DATE else int((group.preeligible&~group.label_defined).sum())),
                       "reason_counts_can_overlap":True,"june_outcomes_available":False})
    return result


def freeze():
    receipt = require_receipt("warehouse_aggregation_receipt.json")
    if (CACHE/"frozen_models.joblib").exists() or (OUT/"warehouse_frozen_contract.json").exists():
        raise SafeFailure("A model/contract is already frozen; do not refreeze after any June outcome access.")
    if (CACHE/"june_access.json").exists() or (CACHE/"june_outcomes.parquet").exists() or (OUT/"warehouse_metrics.json").exists():
        raise SafeFailure("June has been accessed in this study; deleting freeze artifacts does not permit a new freeze.")
    frame = frame_from_cache()
    eligible = frame.loc[frame.preeligible].copy()
    clients = pd.DataFrame({"client":sorted(eligible.client_hash_id.unique())})
    if len(clients)<12: raise SafeFailure("Fewer than twelve history-eligible clients; the predefined grouped design cannot support a useful study.")
    dev,test = next(GroupShuffleSplit(n_splits=1,test_size=.25,random_state=SEED).split(clients,groups=clients.client))
    tr,va = next(GroupShuffleSplit(n_splits=1,test_size=.25,random_state=SEED+1).split(clients.iloc[dev],groups=clients.iloc[dev].client))
    train_clients=set(clients.iloc[dev[tr]].client); val_clients=set(clients.iloc[dev[va]].client); test_clients=set(clients.iloc[test].client)
    assert not(train_clients&val_clients or train_clients&test_clients or val_clients&test_clients)
    train = eligible.loc[eligible.client_hash_id.isin(train_clients)&eligible.decision_date.isin(pd.to_datetime(TRAIN_DATES))&eligible.label_defined]
    validation = eligible.loc[eligible.client_hash_id.isin(val_clients)&eligible.decision_date.eq(pd.Timestamp(VALIDATION_DATE))&eligible.label_defined]
    if train.label.nunique()!=2 or validation.label.nunique()!=2: raise SafeFailure("Training/validation lack both observed outcome classes; no claim or model selection is possible.")
    sampled=fitting_sample(train)
    candidates={name:pipeline(name).fit(sampled[FEATURES],sampled.label.astype(int)) for name in POLICY["candidates"]}
    baseline=PriorRule().fit(train)
    val_scores={"prior_rule":baseline.score(validation),**{name:model.predict_proba(validation[FEATURES])[:,1] for name,model in candidates.items()}}
    val_metrics={name:metrics(validation.label.astype(int),scores) for name,scores in val_scores.items()}
    winner=max(candidates,key=lambda name:val_metrics[name]["average_precision"])
    development=pd.concat([train,validation],ignore_index=True)
    sample=fitting_sample(development)
    final_models={name:pipeline(name).fit(sample[FEATURES],sample.label.astype(int)) for name in candidates}
    final_rule=PriorRule().fit(development)
    frozen={"policy":POLICY,"policy_sha256":contract_hash(),"source_code_sha256":digest(Path(__file__)),
            "development_cache_sha256":receipt["cache_sha256"],"selected_model":winner,
            "clients_cache_sha256":digest(CACHE/"clients.parquet"),
            "validation_metrics":val_metrics,"train_clients":train_clients,"validation_clients":val_clients,
            "test_clients":test_clients,"models":final_models,"baseline":final_rule}
    joblib.dump(frozen,CACHE/"frozen_models.joblib")
    public={"status":"passed","stage":"freeze","revision":REVISION,"policy":POLICY,"run_type":RUN_TYPE,
            "policy_sha256":frozen["policy_sha256"],"source_code_sha256":frozen["source_code_sha256"],
            "selected_model":winner,"validation_metrics":val_metrics,"june_values_accessed":False,
            "model_artifact_sha256":digest(CACHE/"frozen_models.joblib"),
            "clients_cache_sha256":frozen["clients_cache_sha256"],"cohort_flow":cohort_flow(frame),
            "groups":{"train":len(train_clients),"validation":len(val_clients),"test":len(test_clients)},
            "actual_usable_groups":{"train":int(train.client_hash_id.nunique()),"validation":int(validation.client_hash_id.nunique()),
                                    "test_prior_eligible":int(eligible.loc[eligible.client_hash_id.isin(test_clients)&eligible.decision_date.eq(TEST_DATE),"client_hash_id"].nunique())},
            "client_join_audit":frame.attrs["client_join_audit"],
            "fit_rows":{"training_total":len(train),"training_fitted":len(sampled),"development_total":len(development),"development_fitted":len(sample)},
            "temporal_embargo":"last training outcome ends 2026-03-03 < validation decision 2026-04-01; validation outcome ends 2026-05-01 < test decision 2026-06-01",
            "client_groups_defined_from_prior_only_eligibility":True}
    dump(OUT/"warehouse_frozen_contract.json",public)
    print(json.dumps(public,indent=2)); return public


def june_sql(src):
    return f"""WITH daily AS (
      SELECT CAST(report_date AS DATE) report_date,client_hash_id,content_hash_id,COUNT(*) grain_rows,
             ANY_VALUE(gsc_data_available) available,ANY_VALUE(gsc_impressions) impressions
      FROM {src} WHERE report_date>=DATE '2026-06-01' AND report_date<DATE '2026-07-01' GROUP BY 1,2,3
    ) SELECT client_hash_id,content_hash_id,SUM(grain_rows-1) duplicate_grain_excess,
      COUNT(*) FILTER (WHERE available IS TRUE AND impressions IS NOT NULL AND impressions>=0 AND isfinite(impressions)) observed_future,
      SUM(impressions) FILTER (WHERE available IS TRUE AND impressions IS NOT NULL AND impressions>=0 AND isfinite(impressions)) impressions_future
    FROM daily GROUP BY 1,2"""


def evaluate():
    contract=require_receipt("warehouse_frozen_contract.json")
    if (OUT/"warehouse_metrics.json").exists(): raise SafeFailure("June evaluation is already recorded; keep the original final result rather than repeatedly selecting on June.")
    if contract.get("model_artifact_sha256")!=digest(CACHE/"frozen_models.joblib"):
        raise SafeFailure("Frozen model artifact differs from the public freeze receipt; refuse loading/evaluation.")
    frozen=joblib.load(CACHE/"frozen_models.joblib")
    if frozen["policy_sha256"]!=contract_hash() or frozen["source_code_sha256"]!=digest(Path(__file__)):
        raise SafeFailure("Policy or code changed after freeze; June remains sealed. Review the research design rather than silently changing it.")
    if frozen["development_cache_sha256"]!=digest(CACHE/"development_windows.parquet"):
        raise SafeFailure("Development cache changed after freeze; refuse final evaluation.")
    if frozen["clients_cache_sha256"]!=digest(CACHE/"clients.parquet"):
        raise SafeFailure("Client history cache changed after freeze; refuse final eligibility changes.")
    access_path=CACHE/"june_access.json"
    marker={"policy_sha256":frozen["policy_sha256"],"model_artifact_sha256":contract["model_artifact_sha256"],
            "first_access_attempt_utc":datetime.now(timezone.utc).isoformat(),"scope":"marker precedes any June outcome query"}
    if access_path.exists():
        old_marker=json.loads(access_path.read_text(encoding="utf-8"))
        if old_marker.get("policy_sha256")!=marker["policy_sha256"] or old_marker.get("model_artifact_sha256")!=marker["model_artifact_sha256"]:
            raise SafeFailure("June access marker belongs to a different freeze; refuse switching models or contracts.")
    else:
        dump(access_path,marker)
    june_path=CACHE/"june_outcomes.parquet"
    june_receipt_path=CACHE/"june_cache_receipt.json"
    src=relation(paths_for_months({"2026-06"}))
    sql=june_sql(src)
    query_hash=hashlib.sha256(sql.encode()).hexdigest()
    if june_path.exists():
        if not june_receipt_path.exists():
            raise SafeFailure("Existing June cache has no passed integrity receipt; it may be a partial/failed duplicate audit. Do not consume it without researcher repair.")
        june_receipt=json.loads(june_receipt_path.read_text(encoding="utf-8"))
        if (june_receipt.get("status")!="passed" or june_receipt.get("revision")!=REVISION
                or june_receipt.get("query_sha256")!=query_hash or june_receipt.get("cache_sha256")!=digest(june_path)
                or june_receipt.get("policy_sha256")!=frozen["policy_sha256"]
                or june_receipt.get("model_artifact_sha256")!=contract["model_artifact_sha256"]):
            raise SafeFailure("June cache integrity receipt does not match its revision/query/freeze/content; refuse final evaluation.")
        counts=june_receipt["input_audit"]
    else:
        con=connect(remote=True)
        counts=input_audit(con,src)
        cached_query(sql,june_path)
        june_receipt={"status":"passed","revision":REVISION,"policy_sha256":frozen["policy_sha256"],
                      "model_artifact_sha256":contract["model_artifact_sha256"],"query_sha256":query_hash,
                      "cache_sha256":digest(june_path),"input_audit":list(counts)}
        dump(june_receipt_path,june_receipt)
    # Recheck even a hash-bound cache, including the previously failed-copy scenario.
    local=connect()
    checks=local.execute("SELECT COALESCE(SUM(duplicate_grain_excess),0),COUNT(*) FILTER (WHERE client_hash_id IS NULL OR content_hash_id IS NULL) FROM read_parquet(?)",[str(june_path)]).fetchone()
    if checks[0] or checks[1]:
        raise SafeFailure("Cached June outcomes fail local duplicate/key re-audit; do not model this cache.")
    local=connect()
    future=local.execute("SELECT * FROM read_parquet(?)",[str(june_path)]).df()
    frame=frame_from_cache()
    risk=frame.loc[frame.preeligible&frame.decision_date.eq(TEST_DATE)&frame.client_hash_id.isin(frozen["test_clients"])].copy()
    risk=risk.drop(columns=["observed_future","impressions_future","label_defined","label"])
    risk=risk.merge(future.drop(columns="duplicate_grain_excess"),on=["client_hash_id","content_hash_id"],how="left",validate="one_to_one")
    risk=risk.sort_values(["decision_date","client_hash_id","content_hash_id"],kind="stable").reset_index(drop=True)
    future_rate=risk.impressions_future/risk.observed_future.replace(0,np.nan)
    defined=risk.observed_future.ge(24)&np.isfinite(future_rate)&future_rate.ge(0)
    risk["label_defined"]=defined
    risk["label"] = ((future_rate/risk.prior_rate)<.8).astype(int).where(defined)
    test=risk.loc[defined].copy()
    if test.label.nunique()!=2: raise SafeFailure("Final observed outcomes have fewer than two classes; report coverage separately and do not invent discrimination metrics.")
    score_map={"prior_rule":frozen["baseline"].score(test),**{name:model.predict_proba(test[FEATURES])[:,1] for name,model in frozen["models"].items()}}
    results={name:metrics(test.label.astype(int),score) for name,score in score_map.items()}
    winner=frozen["selected_model"]; selected=score_map[winner]
    per_group=[]
    for number,(_,group) in enumerate(test.groupby("client_hash_id",sort=True),start=1):
        positions=test.index.get_indexer(group.index)
        model_metric=metrics(group.label.astype(int),selected[positions]); rule_metric=metrics(group.label.astype(int),score_map["prior_rule"][positions])
        per_group.append({"group":f"Held-out group {number}","rows":len(group),"base_rate":model_metric["base_rate"],
                          "model_ap":model_metric["average_precision"],"rule_ap":rule_metric["average_precision"],
                          "model_auc":model_metric["roc_auc"],"rule_auc":rule_metric["roc_auc"],"effective_k":min(50,len(group)),
                          "both_classes_observed":model_metric["both_classes_observed"]})
    rng=np.random.default_rng(SEED); groups=test.client_hash_id.to_numpy(); unique=np.unique(groups)
    diffs=[]
    for _ in range(200 if len(unique)>=2 else 0):
        chosen=rng.choice(unique,size=len(unique),replace=True)
        indices=np.concatenate([np.flatnonzero(groups==g) for g in chosen]); yy=test.label.to_numpy()[indices].astype(int)
        a=metrics(yy,selected[indices])["average_precision"]; b=metrics(yy,score_map["prior_rule"][indices])["average_precision"]
        if a is not None and b is not None: diffs.append(a-b)
    baseline_receipt=require_receipt("warehouse_aggregation_receipt.json")
    total=int(baseline_receipt["development_fact_rows"])+int(counts[0])
    if total!=78835655: raise SafeFailure("Combined fact count differs from the release manifest; final result withheld for reconciliation.")
    public={"status":"completed actual gated execution","scope":"full warehouse release; prior-only features, future 30-day outcomes, held-out clients","run_type":RUN_TYPE,
            "study_design":"retrospective time-aware backtest with forward-window observed labels; not prospective data collection",
            "as_of_limitation":POLICY["availability_limitation"],
            "source_repository":REPO,"revision":REVISION,"policy_sha256":frozen["policy_sha256"],
            "source_code_sha256":frozen["source_code_sha256"],
            "selected_model":winner,"validation_metrics":frozen["validation_metrics"],"test_metrics":results,
            "development_cohort_flow":contract["cohort_flow"],
            "eligibility":{"predecision_test_candidates":len(risk),"future_labels_defined":len(test),"undefined_future_labels":int((~defined).sum()),
                           "interpretation":"evaluation population requires adequate observed future coverage; attrition can bias measured results; no positive-future-volume filter"},
            "fact_metadata_reconciliation":{"daily_rows":total,"expected_rows":78835655,"june_rows":int(counts[0]),
                                            "june_min_date":str(counts[1]),"june_max_date":str(counts[2])},
            "metric_quality":{"june_null_dates_or_keys":int(counts[3]),"june_unusable_impression_metrics":int(counts[4]),
                              "june_unusable_click_metrics":int(counts[5]),"invalid_measurements_treated_as_unobserved":True},
            "per_client_metrics":per_group,
            "macro_client_model_ap":(float(np.mean([g["model_ap"] for g in per_group if g["model_ap"] is not None])) if any(g["model_ap"] is not None for g in per_group) else None),
            "macro_client_rule_ap":(float(np.mean([g["rule_ap"] for g in per_group if g["rule_ap"] is not None])) if any(g["rule_ap"] is not None for g in per_group) else None),
            "macro_ap_groups_used":sum(g["both_classes_observed"] for g in per_group),
            "macro_ap_single_class_groups_excluded":sum(not g["both_classes_observed"] for g in per_group),
            "june_cache_sha256":june_receipt["cache_sha256"],
            "client_bootstrap_ap_difference_95":([float(np.quantile(diffs,.025)),float(np.quantile(diffs,.975))] if diffs else None),
            "bootstrap_resamples":200,"test_client_groups":len(unique),"causal_claim":False,
            "bootstrap_completed_draws":len(diffs),
            "bootstrap_caveat":("insufficient independent test clients; no interval" if len(unique)<2 else
                                 "client-cluster percentile interval; limited client count and selected outcome coverage constrain uncertainty"),
            "environment":{name:importlib.metadata.version(name) for name in ["duckdb","huggingface_hub","numpy","pandas","scikit-learn"]}}
    all_scores=frozen["models"][winner].predict_proba(risk[FEATURES])[:,1]
    recommendations=[]; lookup=[]
    for rank,pos in enumerate(np.argsort(-all_scores,kind="stable")[:20],start=1):
        row=risk.iloc[pos]; reasons=["prior_only_model_future_decline_score"]
        if row.prior_momentum_pct < -20: reasons.append("prior_impression_decline")
        if pd.notna(row.position30) and row.position30<=20 and row.ctr90_pct<.5: reasons.append("low_ctr_measured_position")
        if not row.has_position: reasons.append("position_measurement_missing")
        case=f"Warehouse review W{rank:02d}"
        recommendations.append({"rank":rank,"case":case,"score":round(float(all_scores[pos]),4),"reason_codes":reasons,
                                "action":"Verify current search evidence, measurement and page/query relevance before editing",
                                "confidence":"observational future-outcome association; editorial benefit unvalidated"})
        lookup.append({"case":case,"client_hash_id":row.client_hash_id,"content_hash_id":row.content_hash_id})
    pd.DataFrame(lookup).to_csv(CACHE/"recommendation_lookup.csv",index=False)
    dump(OUT/"warehouse_metrics.json",public)
    dump(OUT/"warehouse_ranked_actions.json",{"scope":"all prior-eligible held-out clients, without selecting on June label coverage","recommendations":recommendations})
    report=f"""# Warehouse extension: retrospective time-aware signal backtest\n\nThis report was generated only after actual gated execution. Source: {REPO}, revision `{REVISION}`. Features use report dates strictly prior to 2026-06-01; June 1–30 is the observed forward-window outcome and test clients were absent from development. Historical ingestion/as-of vintages are unavailable, so real-time finalization at each decision date is an assumption; this is not prospective live data collection. Contract SHA-256: `{frozen['policy_sha256']}`.\n\nValidation-selected method: {winner}. Test base rate: {results[winner]['base_rate']:.4f}; model AP {results[winner]['average_precision']:.4f}, rule AP {results['prior_rule']['average_precision']:.4f}; model precision@50 {results[winner]['precision_at_50']:.4f}, rule {results['prior_rule']['precision_at_50']:.4f}.\n\nPrior-eligible test candidates: {len(risk):,}; adequately observed outcome labels: {len(test):,}; undefined labels: {int((~defined).sum()):,}. The outcome-observed subset is a selection limit. Prior-only risk recommendations include undefined-outcome candidates and never use future labels as inputs.\n\nThe rule is a new historical-momentum/visibility/position comparator, not the starter freshness/depth rule. No current dim_content or fixed-window query facts are used. Client bootstrap uncertainty, macro metrics (excluding single-class discrimination), effective K, cohort-flow counts and environment are recorded in `work/outputs/warehouse_metrics.json`; recommendations are bounded and synthetic-ID-safe. Source and executed notebook provide reproduction. No refresh intervention, causal benefit or Google algorithm claim is established.\n\n[Built on the FlyRank ML Internship dataset](https://flyrank.ai). The original starter paper remains distinct; integrate this genuine extension only after intern/editor review.\n"""
    (EXTENSION/"warehouse_report.md").write_text(report,encoding="utf-8")
    print(json.dumps(public,indent=2)); return public


def self_check():
    """Synthetic integrity checks only, never warehouse metrics or empirical claims."""
    con=connect()
    dates=pd.date_range("2026-03-03","2026-06-30",freq="D")
    fixture=pd.DataFrame({"report_date":dates,"client_hash_id":"synthetic-client","content_hash_id":"synthetic-content",
                          "gsc_data_available":True,"gsc_impressions":100.,"gsc_clicks":2.,"gsc_avg_position":10.})
    con.register("fixture",fixture)
    first=con.sql(aggregation_sql("fixture",["2026-06-01"])).df()
    assert first.observed90.iloc[0]==90 and first.observed30.iloc[0]==30
    assert first.impressions90.iloc[0]==9000 and first.observed_future.iloc[0]==0
    fixture.loc[fixture.report_date>=TEST_DATE,"gsc_impressions"]=999999.
    con.unregister("fixture"); con.register("fixture",fixture)
    altered=con.sql(aggregation_sql("fixture",["2026-06-01"])).df()
    pd.testing.assert_frame_equal(first,altered)
    fixture.loc[fixture.report_date>=TEST_DATE,"gsc_data_available"]=False
    con.unregister("fixture"); con.register("fixture",fixture)
    target=con.sql(june_sql("fixture")).df()
    assert target.observed_future.iloc[0]==0 and pd.isna(target.impressions_future.iloc[0])
    fixture.loc[fixture.report_date>=TEST_DATE,"gsc_data_available"]=True
    fixture.loc[fixture.report_date>=TEST_DATE,"gsc_impressions"]=0.
    con.unregister("fixture"); con.register("fixture",fixture)
    target=con.sql(june_sql("fixture")).df()
    assert target.observed_future.iloc[0]==30 and target.impressions_future.iloc[0]==0
    fixture.loc[fixture.report_date.eq(TEST_DATE),"gsc_impressions"]=np.inf
    con.unregister("fixture"); con.register("fixture",fixture)
    target=con.sql(june_sql("fixture")).df()
    assert target.observed_future.iloc[0]==29 and target.impressions_future.iloc[0]==0
    fixture=pd.concat([fixture,fixture.iloc[[0]]],ignore_index=True)
    con.unregister("fixture"); con.register("fixture",fixture)
    duplicate=con.sql(aggregation_sql("fixture",["2026-06-01"])).df()
    assert duplicate.duplicate_grain_excess.iloc[0]==1
    fixture.loc[0,"client_hash_id"]=None
    con.unregister("fixture"); con.register("fixture",fixture)
    try: input_audit(con,"fixture")
    except SafeFailure: pass
    else: raise AssertionError("Missing synthetic key did not halt the audit.")
    print("Synthetic checks passed: exact half-open windows, future perturbation invariance, missing-vs-zero outcome, nonfinite metric exclusion, null-key guard and duplicate detection. No warehouse results generated.")
    return {"status":"synthetic integrity checks passed","warehouse_execution":False}


def configure_replay(name):
    """Fresh clones replay in isolation; never overwrite a recorded original holdout."""
    global OUT,CACHE,EXTENSION,RUN_TYPE
    if len(name)>64 or not name.replace("-","").replace("_","").isalnum():
        raise SafeFailure("Replay name must contain only letters, digits, hyphens or underscores, at most 64 characters.")
    replay_root=ROOT/"work/outputs/warehouse_replays"
    replay_root.mkdir(parents=True,exist_ok=True)
    (replay_root/".gitignore").write_text("*\n!.gitignore\n",encoding="utf-8")
    OUT=replay_root/name; CACHE=OUT/"private_cache"; EXTENSION=OUT
    RUN_TYPE="isolated reproduction of the immutable design; previously observed June is not new validation"


def completed_stage(stage):
    """Reuse verifiable real execution receipts, never a template or a bare cache."""
    mapping={"inspect":("warehouse_schema_audit.json","clients.parquet","clients_cache_sha256"),
             "develop":("warehouse_development_receipt.json","march_development.parquet","cache_sha256"),
             "aggregate":("warehouse_aggregation_receipt.json","development_windows.parquet","cache_sha256"),
             "freeze":("warehouse_frozen_contract.json","frozen_models.joblib","model_artifact_sha256"),
             "evaluate":("warehouse_metrics.json","june_outcomes.parquet","june_cache_sha256")}
    if stage not in mapping: return None
    receipt_name,cache_name,field=mapping[stage]
    receipt_path=OUT/receipt_name; cache_path=CACHE/cache_name
    if not receipt_path.exists() or not cache_path.exists(): return None
    receipt=json.loads(receipt_path.read_text(encoding="utf-8"))
    valid_status=receipt.get("status")=="passed" or (stage=="evaluate" and receipt.get("status")=="completed actual gated execution")
    if (not valid_status or receipt.get("revision")!=REVISION or receipt.get(field)!=digest(cache_path)
            or receipt.get("source_code_sha256")!=digest(Path(__file__))):
        raise SafeFailure("Existing stage receipt/cache/code does not match; review it rather than silently replay or overwrite.")
    return receipt


def compare_replay():
    if RUN_TYPE.startswith("original"):
        raise SafeFailure("Comparison requires --replay NAME; original warehouse artifacts remain unchanged.")
    original_path=ROOT/"work/outputs/warehouse_metrics.json"
    if not original_path.exists() or not (OUT/"warehouse_metrics.json").exists():
        raise SafeFailure("Original and replay warehouse metrics must both genuinely exist before comparison.")
    original=json.loads(original_path.read_text(encoding="utf-8")); replay=json.loads((OUT/"warehouse_metrics.json").read_text(encoding="utf-8"))
    if original.get("policy_sha256")!=contract_hash() or replay.get("policy_sha256")!=contract_hash():
        raise SafeFailure("Replay policy differs from recorded original; it is not a reproduction of that experiment.")
    if original.get("source_code_sha256")!=digest(Path(__file__)) or replay.get("source_code_sha256")!=digest(Path(__file__)):
        raise SafeFailure("Original/replay source-code hashes differ from this script; refuse an exact-reproduction label.")
    matching=all(original[key]==replay[key] for key in ["selected_model","validation_metrics","test_metrics","eligibility"])
    result={"status":"exact metric reproduction" if matching else "differences require investigation; do not retune on June",
            "same_policy":True,"new_validation":False,"same_environment":original.get("environment")==replay.get("environment")}
    dump(OUT/"reproduction_comparison.json",result)
    print(json.dumps(result,indent=2)); return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage",required=True,choices=["plan","self-check","inspect","develop","aggregate","freeze","evaluate","compare"])
    parser.add_argument("--replay",help="Isolated run name for reproducing an existing immutable study; never fresh validation.")
    args=parser.parse_args()
    if args.replay:
        try: configure_replay(args.replay)
        except SafeFailure as exc:
            print(f"PENDING / STOPPED: {exc}"); raise SystemExit(2) from None
    if args.stage=="plan":
        print(json.dumps({"status":"prepared specification; gated execution pending","policy_sha256":contract_hash(),"policy":POLICY},indent=2)); return
    stages={"self-check":self_check,"inspect":inspect,"develop":develop,"aggregate":aggregate,"freeze":freeze,"evaluate":evaluate,"compare":compare_replay}
    try:
        prior=completed_stage(args.stage)
        if prior is not None:
            print("Reusing a verified completed stage; no new remote scan or new validation.")
            print(json.dumps(prior,indent=2)); return
        stages[args.stage]()
    except SafeFailure as exc:
        print(f"PENDING / STOPPED: {exc}")
        raise SystemExit(2) from None
    except Exception:
        print("PENDING / STOPPED: unexpected execution failure; details suppressed to protect credentials and identifying rows. No result may be claimed without a completed stage receipt.")
        raise SystemExit(2) from None


if __name__=="__main__": main()
