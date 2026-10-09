"""Reproduce the starter-scoped refresh review study; no warehouse access assumed.

Run from the repository root: python work/scripts/capstone_analysis.py
Only public aggregates/charts and a bounded recommendation demonstration are saved.
The operational pseudonym lookup is local-only CSV (ignored by the repository).
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
from urllib.parse import urlparse

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score, precision_recall_curve
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "work" / "outputs"
FIG = ROOT / "work" / "figures"
SEED = 2026
NUMERIC = [
    "search_volume", "competition", "cpc", "word_count", "log_impressions_90d",
    "log_clicks_90d", "log_sessions_90d", "days_with_impressions", "days_with_sessions",
    "content_age_days", "days_since_last_update", "ctr", "avg_position",
    "engagement_rate", "scroll_rate", "has_keyword_data", "has_word_count", "has_position",
    "has_scroll_measurement",
]
CATEGORICAL = ["content_type", "competition_level", "main_intent"]
FEATURES = NUMERIC + CATEGORICAL
BANNED = {
    "content_id", "client_id", "trend_direction", "trend_pct", "is_declining_label",
    "impressions_last_30d", "clicks_last_30d", "sessions_last_30d",
    "impressions_prev_30d", "clicks_prev_30d", "sessions_prev_30d",
    "provider_used", "model_used",
}


def save_json(name, payload):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(json.dumps(payload, indent=2, allow_nan=False), encoding="utf-8")


def publication_state():
    """Read a checked local publication receipt; never infer deployment from a draft URL."""
    path = ROOT / "work" / "site" / "publication.json"
    if not path.exists():
        return {"verified": False, "basis": "no local publication receipt"}
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
        urls = [record.get("paper_url", ""), record.get("repository_url", "")]
        valid_urls = all(isinstance(url, str) and urlparse(url).scheme == "https" and urlparse(url).hostname
                         and not urlparse(url).username for url in urls)
        verified = bool(record.get("status") == "succeeded" and record.get("access") == "public"
                        and record.get("verified_at_utc") and record.get("source_commit") and valid_urls)
        return {"verified": verified, "paper_url": urls[0], "repository_url": urls[1],
                "verified_at_utc": record.get("verified_at_utc"),
                "basis": "validated local publication receipt; notebook reruns do not republish or claim portal submission"}
    except (OSError, ValueError, TypeError):
        return {"verified": False, "basis": "local publication receipt could not be validated"}


def load_data():
    path = ROOT / "data" / "raw" / "content_refresh_anonymized.csv"
    raw = pd.read_csv(path)
    assert raw.shape == (30000, 44), "Starter contract changed; inspect before rerunning."
    assert raw.client_id.nunique() == 32
    assert not raw.content_id.duplicated().any(), "Duplicate content grain."
    assert not raw.duplicated(["client_id", "content_id"]).any()
    frame = raw.loc[(raw.impressions_90d > 0) & (raw.content_age_days >= 90)].copy()
    frame = frame.reset_index(drop=True)
    y = frame.trend_direction.str.lower().eq("down").astype(int)
    x = frame.copy()
    x["has_keyword_data"] = x.search_volume.notna().astype(int)
    x["has_word_count"] = x.word_count.notna().astype(int)
    x["has_position"] = x.avg_position.gt(0).astype(int)
    x["has_scroll_measurement"] = x.scroll_rate.notna().astype(int)
    x["avg_position"] = x.avg_position.mask(x.avg_position.eq(0))
    for field in ["impressions_90d", "clicks_90d", "sessions_90d"]:
        x["log_" + field] = np.log1p(x[field].clip(lower=0))
    x = x[FEATURES].replace([np.inf, -np.inf], np.nan)
    for field in CATEGORICAL:
        x[field] = x[field].fillna("unknown").astype(str)
    assert not set(x.columns) & BANNED
    summary = {
        "rows": int(len(raw)), "columns": int(raw.shape[1]), "clients": int(raw.client_id.nunique()),
        "eligible_rows": int(len(frame)), "declining_rows": int(y.sum()),
        "declining_share": float(y.mean()),
        "stale_visible_rows": int(((raw.days_since_last_update >= 180) & (raw.impressions_90d >= 500)).sum()),
        "visible_rows_500": int((raw.impressions_90d >= 500).sum()),
        "no_position_rows": int(raw.avg_position.eq(0).sum()),
        "missing_word_count_rows": int(raw.word_count.isna().sum()),
        "missing_keyword_rows": int(raw.search_volume.isna().sum()),
        "scroll_rate_above_100_rows": int(raw.scroll_rate.gt(100).sum()),
        "ai_traffic_pct_above_100_rows": int(raw.ai_traffic_pct.gt(100).sum()),
        "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "time_scope": "trailing 90 days at starter export; calendar end not supplied in starter dictionary",
    }
    return frame, x, y, summary


class RuleBaseline:
    """Reference-style weights with all empirical distributions fitted on training only."""
    def fit(self, frame):
        self.impressions = np.sort(np.log1p(frame.impressions_90d.to_numpy()))
        self.freshness = np.sort(frame.days_since_last_update.dropna().to_numpy())
        self.depth = np.sort(frame.word_count.dropna().to_numpy())
        return self

    @staticmethod
    def cdf(reference, values):
        return np.searchsorted(reference, values, side="right") / len(reference)

    def score(self, frame):
        visibility = self.cdf(self.impressions, np.log1p(frame.impressions_90d.to_numpy()))
        freshness = self.cdf(self.freshness, frame.days_since_last_update.fillna(0).to_numpy())
        position = frame.avg_position.to_numpy()
        position_opportunity = (1 - (np.clip(position, 1, 50) - 1) / 49) * visibility * (position > 0)
        depth_gap = (1 - self.cdf(self.depth, frame.word_count.fillna(np.inf).to_numpy())) * visibility
        return np.clip(.40 * visibility + .30 * freshness + .25 * position_opportunity + .05 * depth_gap, 0, 1)


def model_pipeline(kind, numeric=NUMERIC, categorical=CATEGORICAL):
    numeric_steps = [("impute", SimpleImputer(strategy="median"))]
    if kind == "logistic_regression":
        numeric_steps.append(("scale", StandardScaler()))
    pre = ColumnTransformer([
        ("numeric", Pipeline(numeric_steps), numeric),
        ("categorical", Pipeline([
            ("impute", SimpleImputer(strategy="most_frequent")),
            ("encode", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]), categorical),
    ])
    if kind == "logistic_regression":
        classifier = LogisticRegression(max_iter=1500, C=1., random_state=SEED)
    else:
        classifier = RandomForestClassifier(n_estimators=180, max_depth=10, min_samples_leaf=25,
                                           max_features="sqrt", n_jobs=-1, random_state=SEED)
    return Pipeline([("preprocess", pre), ("model", classifier)])


def metrics(y, score):
    labels = np.asarray(y)
    scores = np.asarray(score)
    order = np.argsort(-scores, kind="stable")
    base = float(labels.mean())
    result = {"rows": int(len(labels)), "base_rate": base,
              "majority_class_accuracy": max(base, 1-base),
              "both_classes_observed": bool(len(np.unique(labels)) == 2),
              "roc_auc": float(roc_auc_score(labels, scores)) if len(np.unique(labels)) == 2 else None,
              "average_precision": float(average_precision_score(labels, scores)) if labels.sum() else None}
    for k in [50, 100, 250]:
        n = min(k, len(labels))
        p = float(labels[order[:n]].mean())
        result[f"precision_at_{k}"] = p
        result[f"effective_k_at_{k}"] = n
        result[f"lift_at_{k}_vs_base_rate"] = p / base if base else None
    return result


def cluster_bootstrap(y, scores, baseline, groups, iterations=400):
    rng = np.random.default_rng(SEED)
    unique = np.unique(groups)
    samples = {"average_precision_difference": [], "precision_at_50_difference": []}
    for _ in range(iterations):
        drawn = rng.choice(unique, size=len(unique), replace=True)
        indices = np.concatenate([np.flatnonzero(groups == group) for group in drawn])
        a = metrics(y[indices], scores[indices])
        b = metrics(y[indices], baseline[indices])
        samples["average_precision_difference"].append(a["average_precision"] - b["average_precision"])
        samples["precision_at_50_difference"].append(a["precision_at_50"] - b["precision_at_50"])
    return {
        "resamples": iterations, "clusters": int(len(unique)), "seed": SEED,
        "method": "resample held-out clients with replacement, retaining all their rows; percentile interval",
        "limitation": "only eight held-out client clusters; intervals do not establish future or causal performance",
        **{key: {"lower_95": float(np.quantile(values, .025)), "upper_95": float(np.quantile(values, .975))}
           for key, values in samples.items()},
    }


def action_codes(row, score):
    reasons = []
    if row.days_since_last_update >= 180:
        reasons.append("stale_visible_content")
    if 0 < row.avg_position <= 20 and row.ctr < .5:
        reasons.append("low_ctr_review")
    if pd.notna(row.word_count) and 0 < row.word_count < 1200:
        reasons.append("depth_review")
    if row.sessions_90d >= 30 and (row.engagement_rate < 30 or (pd.notna(row.scroll_rate) and row.scroll_rate < 30)):
        reasons.append("engagement_review")
    if row.avg_position == 0:
        reasons.append("position_missing")
    if pd.isna(row.word_count):
        reasons.append("depth_measurement_missing")
    reasons.append("model_associated_with_current_decline_proxy")
    if "position_missing" in reasons:
        action = "Check search measurement before editing"
    elif "low_ctr_review" in reasons:
        action = "Review title, description and query intent"
    elif "depth_review" in reasons:
        action = "Review coverage and factual freshness"
    elif "stale_visible_content" in reasons:
        action = "Check accuracy and freshness; edit only if needed"
    elif "engagement_review" in reasons:
        action = "Inspect layout, relevance and analytics instrumentation"
    else:
        action = "Inspect current search evidence and monitor"
    return action, reasons


def plots(y, score_map, importance, queue):
    FIG.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})
    colors = ["#a06a36", "#527ea3", "#216e60"]
    fig, ax = plt.subplots(figsize=(9, 5))
    for (name, score), color in zip(score_map.items(), colors):
        p, r, _ = precision_recall_curve(y, score)
        ax.plot(r, p, label=f"{name.replace('_', ' ')} (AP {average_precision_score(y, score):.3f})", color=color)
    ax.axhline(np.mean(y), linestyle="--", color="gray", label=f"Base rate {np.mean(y):.3f}")
    ax.set(xlabel="Recall of current-window decline proxy", ylabel="Precision", ylim=(0, 1.03),
           title="Client-held-out evaluation: contemporaneous proxy")
    ax.legend(loc="lower left", fontsize=9)
    fig.tight_layout(); fig.savefig(FIG / "capstone_precision_recall.png", dpi=170); plt.close(fig)
    fig, ax = plt.subplots(figsize=(9, 5))
    ks = [10, 25, 50, 100, 250, 500]
    for (name, score), color in zip(score_map.items(), colors):
        order = np.argsort(-score, kind="stable")
        ax.plot(ks, [np.asarray(y)[order[:k]].mean() for k in ks], marker="o", label=name.replace('_', ' '), color=color)
    ax.axhline(np.mean(y), linestyle="--", color="gray", label="Holdout base rate")
    ax.set(xlabel="Review budget K", ylabel="Precision among top K", ylim=(0, 1.03),
           title="Sensitivity to editor review budget")
    ax.legend(fontsize=9); fig.tight_layout(); fig.savefig(FIG / "capstone_review_budget.png", dpi=170); plt.close(fig)
    top = pd.DataFrame(importance).sort_values("ap_drop_mean", ascending=False).head(10).iloc[::-1]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(top.feature, top.ap_drop_mean, xerr=top.ap_drop_std, color="#216e60")
    ax.set(xlabel="Drop in validation average precision after permutation", title="Feature association audit (validation only)")
    fig.tight_layout(); fig.savefig(FIG / "capstone_feature_audit.png", dpi=170); plt.close(fig)
    actions = pd.Series([item["action"] for item in queue]).value_counts()
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(actions.index[::-1], actions.values[::-1], color="#527ea3")
    ax.set(xlabel="Cases among first 20 eligible review recommendations", title="Human review actions, not automatic refresh orders")
    fig.tight_layout(); fig.savefig(FIG / "capstone_actions.png", dpi=170); plt.close(fig)


def run_study():
    frame, x, y, summary = load_data()
    groups = frame.client_id
    dev, test = next(GroupShuffleSplit(n_splits=1, test_size=.25, random_state=SEED).split(x, y, groups))
    train_local, validation_local = next(GroupShuffleSplit(n_splits=1, test_size=.25, random_state=SEED+1).split(
        x.iloc[dev], y.iloc[dev], groups.iloc[dev]))
    train, validation = dev[train_local], dev[validation_local]
    partitions = {"train": train, "validation": validation, "test": test}
    group_sets = {name: set(groups.iloc[index]) for name, index in partitions.items()}
    assert not (group_sets["train"] & group_sets["validation"])
    assert not (group_sets["train"] & group_sets["test"])
    assert not (group_sets["validation"] & group_sets["test"])
    assert len(set(train) | set(validation) | set(test)) == len(frame)
    split_summary = {name: {"rows": int(len(index)), "clients": int(groups.iloc[index].nunique()),
                           "proxy_base_rate": float(y.iloc[index].mean())} for name, index in partitions.items()}
    save_json("research_question_numbers.json", summary)
    baseline = RuleBaseline().fit(frame.iloc[train])
    val_scores = {"rule_baseline": baseline.score(frame.iloc[validation])}
    models = {}
    for name in ["logistic_regression", "random_forest"]:
        model = model_pipeline(name).fit(x.iloc[train], y.iloc[train])
        models[name] = model
        val_scores[name] = model.predict_proba(x.iloc[validation])[:, 1]
    val_metrics = {name: metrics(y.iloc[validation], score) for name, score in val_scores.items()}
    winner = max(models, key=lambda name: val_metrics[name]["average_precision"])
    pi = permutation_importance(models[winner], x.iloc[validation], y.iloc[validation],
                                scoring="average_precision", n_repeats=4, random_state=SEED, n_jobs=1)
    importance = [{"feature": name, "ap_drop_mean": float(mean), "ap_drop_std": float(std)}
                  for name, mean, std in zip(FEATURES, pi.importances_mean, pi.importances_std)]
    # A train-only shuffled-label control is evaluated on validation only.
    rng = np.random.default_rng(SEED)
    shuffled_model = clone(models[winner]).fit(x.iloc[train], rng.permutation(y.iloc[train].to_numpy()))
    shuffle_metrics = metrics(y.iloc[validation], shuffled_model.predict_proba(x.iloc[validation])[:, 1])
    # Fixed ablation asks how much association remains without contemporaneous traffic/rate signals.
    metadata_features = ["search_volume", "competition", "cpc", "word_count", "content_age_days",
                         "days_since_last_update", "has_keyword_data", "has_word_count"]
    metadata_model = model_pipeline(winner, numeric=metadata_features).fit(x.iloc[dev], y.iloc[dev])
    # Model selection is completed before any test prediction. Hyperparameters are fixed above.
    final_models = {name: clone(model).fit(x.iloc[dev], y.iloc[dev]) for name, model in models.items()}
    baseline = RuleBaseline().fit(frame.iloc[dev])
    test_scores = {"rule_baseline": baseline.score(frame.iloc[test]),
                   **{name: model.predict_proba(x.iloc[test])[:, 1] for name, model in final_models.items()}}
    test_metrics = {name: metrics(y.iloc[test], score) for name, score in test_scores.items()}
    metadata_metrics = metrics(y.iloc[test], metadata_model.predict_proba(x.iloc[test])[:, 1])
    eligible = frame.iloc[test].impressions_90d.ge(500).to_numpy()
    eligible_metrics = {name: metrics(y.iloc[test].to_numpy()[eligible], score[eligible]) for name, score in test_scores.items()}
    selected_scores = test_scores[winner]
    uncertainty = cluster_bootstrap(y.iloc[test].to_numpy(), selected_scores, test_scores["rule_baseline"], groups.iloc[test].to_numpy())
    per_client = []
    test_groups = groups.iloc[test].to_numpy()
    for code, group in enumerate(sorted(set(test_groups)), start=1):
        mask = test_groups == group
        m = metrics(y.iloc[test].to_numpy()[mask], selected_scores[mask])
        b = metrics(y.iloc[test].to_numpy()[mask], test_scores["rule_baseline"][mask])
        per_client.append({"group": f"Held-out group {code}", "rows": m["rows"], "base_rate": m["base_rate"],
                           "model_ap": m["average_precision"], "baseline_ap": b["average_precision"],
                           "model_roc_auc": m["roc_auc"], "baseline_roc_auc": b["roc_auc"]})
    subgroups = []
    test_frame = frame.iloc[test].reset_index(drop=True)
    subgroup_masks = {
        "position unavailable": test_frame.avg_position.eq(0),
        "word count missing": test_frame.word_count.isna(),
        "word count observed": test_frame.word_count.notna(),
        "impressions below 500": test_frame.impressions_90d.lt(500),
        "impressions at least 500": test_frame.impressions_90d.ge(500),
    }
    for name, mask in subgroup_masks.items():
        indices = mask.to_numpy()
        m = metrics(y.iloc[test].to_numpy()[indices], selected_scores[indices])
        subgroups.append({"stratum": name, **m})
    order = np.flatnonzero(eligible)[np.argsort(-selected_scores[eligible], kind="stable")]
    ranked = []
    private_map = []
    for rank, local_idx in enumerate(order[:20], start=1):
        row = test_frame.iloc[local_idx]
        action, reasons = action_codes(row, selected_scores[local_idx])
        case = f"Review case R{rank:02d}"
        ranked.append({"rank": rank, "case": case, "review_score": round(float(selected_scores[local_idx]), 4),
                       "action": action, "reason_codes": reasons,
                       "confidence": "unvalidated editorial action; score is a current-proxy ranking, not causal benefit"})
        private_map.append({"case": case, "content_id": row.content_id, "client_id": row.client_id,
                            "action": action, "reason_codes": "|".join(reasons)})
    # The target is used only here for error analysis, never in the action generation above.
    top50 = np.argsort(-selected_scores, kind="stable")[:50]
    positives = int(y.iloc[test].to_numpy()[top50].sum())
    audit = {
        "ids_excluded_from_features": True, "trend_fields_excluded": True,
        "all_six_30_day_trend_input_fields_excluded": True, "client_overlap_between_partitions": 0,
        "imputation_scaling_encoding_fitted_on_train": True,
        "final_refit_scope": "train plus validation clients, never test clients",
        "baseline_empirical_cdfs_fit_scope": "development clients for final test; training clients for validation",
        "label_shuffling_control": {"split": "validation only", **shuffle_metrics},
        "no_future_validation": "90-day feature totals overlap the label window; only contemporaneous held-client discrimination is measured",
        "rule_label_limitation": "trend_direction down is a deterministic bucket of measured impression change, not editorial usefulness",
        "source_grain_duplicates": 0,
    }
    publication = publication_state()
    pending = ["approved Hugging Face access and local HF_TOKEN", "full warehouse feature and future-outcome construction",
               "client/time-aware warehouse evaluation", "intern/editor review", "actual internship portal submission after review"]
    if not publication["verified"]:
        pending.append("owned public repository and verified deployed paper URL")
    result = {
        "study": "Ranking Signal Analysis: explainable content-review priorities", "date": "2026-10-09",
        "status": ("starter study and public paper complete; full-warehouse study, intern/editor review and portal submission pending"
                   if publication["verified"] else
                   "starter study complete; full-warehouse study, intern/editor review, public publication and portal submission pending"),
        "publication": publication,
        "data": summary, "target": "trend_direction == down; contemporaneous proxy, not future decline",
        "feature_columns": FEATURES, "excluded_columns": sorted(BANNED), "random_seed": SEED,
        "split": split_summary, "split_design": "25% held-out client test; 25% of remaining clients validation; no row-random split",
        "model_parameters": {"logistic_regression": {"C": 1., "max_iter": 1500},
                             "random_forest": {"n_estimators": 180, "max_depth": 10, "min_samples_leaf": 25, "max_features": "sqrt"}},
        "baseline_formula": ".40 training-CDF(log impressions) + .30 training-CDF(freshness days) + .25 visibility*(50-clipped_position)/49 + .05 visibility*depth_gap; missing position/depth receive no opportunity bonus",
        "model_selection": "highest validation average precision among two fixed candidates; no test selection",
        "selected_model": winner, "validation_metrics": val_metrics, "test_metrics": test_metrics,
        "review_eligible_test_metrics": eligible_metrics, "review_eligibility": "test pages with at least 500 trailing-90-day impressions",
        "client_bootstrap_intervals": uncertainty, "per_client_metrics": per_client,
        "macro_client_model_ap": float(np.mean([item["model_ap"] for item in per_client])),
        "macro_client_baseline_ap": float(np.mean([item["baseline_ap"] for item in per_client])),
        "subgroup_metrics": subgroups,
        "metadata_only_ablation": {"numeric_features": metadata_features, "categorical_features": CATEGORICAL,
                                   "metrics": metadata_metrics,
                                   "interpretation": "removes contemporaneous traffic totals, coverage and rates; still observational metadata, not a prospective test"},
        "error_analysis": {"top_50_proxy_positive": positives, "top_50_proxy_negative": 50-positives,
                           "meaning": "proxy-negative cases are not proven wasted edits; a proxy-positive case is not proven useful to refresh"},
        "leakage_audit": audit,
        "environment": {package: importlib.metadata.version(package) for package in ["numpy", "pandas", "scikit-learn", "matplotlib"]},
        "pending_requirements": pending,
    }
    save_json("capstone_metrics.json", result)
    save_json("capstone_feature_audit.json", importance)
    save_json("capstone_ranked_actions.json", {"scope": "bounded demonstration from held-out starter pages; no automatic changes", "recommendations": ranked})
    save_json("capstone_leakage_audit.json", audit)
    pd.DataFrame(private_map).to_csv(OUT / "capstone_local_case_lookup.csv", index=False)
    plots(y.iloc[test].to_numpy(), test_scores, importance, ranked)
    print(json.dumps({"rows": summary["rows"], "selected_model": winner, "test_metrics": test_metrics,
                      "split": split_summary, "warehouse_status": "pending authenticated access"}, indent=2))
    return result


if __name__ == "__main__":
    argparse.ArgumentParser(description=__doc__).parse_args()
    run_study()
