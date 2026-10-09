# Analysis card: Ranking Signal Analysis

Author: Hamza Afzal. Date: 9 October 2026.

**Purpose.** Describe associations between safe content/current-window search signals and observed impression decline, and prioritize human review. A score is not a probability that refreshing will improve traffic. Automatic editing, pruning and claims about Google's algorithm are outside the supported use.

**Data.** Local 30,000-row starter CSV, one pseudonymized content item per row, 32 clients, trailing-90-day aggregates. All rows pass positive-impression and age-at-least-90 filters. Calendar export end is not supplied. Full warehouse analysis is pending access.

**Target.** `trend_direction == down`, a thresholded current-window impression-change proxy. The direct source fields and all six last/previous-30-day inputs are excluded. The remaining 90-day traffic features overlap the proxy window, so results remain contemporaneous association.

**Model.** Logistic regression, C=1, 1,500-iteration cap, median imputation, standardized numeric features, one-hot categories. It was selected by validation average precision from two fixed candidates; the alternative forest uses 180 trees, depth 10 and minimum leaf size 25. IDs, provider/model labels, trend inputs and redundant derived tiers never enter the features. Missing keyword/depth/position/scroll observations are explicit flags; position zero becomes missing.

**Validation.** GroupShuffleSplit by client: 18 training clients/24,099 rows, six validation clients/1,766 rows, and eight final test clients/4,135 rows. Seeds 2026 and 2027. Selection occurs on validation AP; final models and baseline transformations are refitted on development clients only. This is a fixed held-out evaluation, not a claim of an independently witnessed blind experiment.

**Measured comparison.** Selected logistic test AP 0.6767, ROC AUC 0.5972 and precision@50 0.80; rule AP 0.5976, ROC AUC 0.5296 and precision@50 0.42. Test proxy base rate is 0.5956. The practical >=500-impression subset contains 1,177 test pages; selected-model precision@50 is 0.72 and rule precision@50 is 0.42. Values and exact package versions live in `work/outputs/capstone_metrics.json`.

**Negative evidence.** The metadata-only ablation has AP 0.5722 and ROC AUC 0.4828. Model AP is lower than baseline AP for one of eight held-out clients. The validation-selected logistic model has lower test AP than the forest; it is retained because selection must not use final test results. The study does not justify freshness or article depth as causal ranking factors.

**Risks and limits.** Availability indicators and current traffic drive part of the association. The no-position test stratum contains only 20 rows and no positive proxy labels; discrimination metrics there are undefined. Eight test clients limit uncertainty estimation. Data missingness, measurement systems, client imbalance, seasonality, unsupported content-text interpretation and proxy utility all limit deployment.

**Human use.** Inspect the reason-coded first 20 candidates, confirm data quality, then check the actual page and query context in an authorized system before any edit. Public artifacts use synthetic case labels; the local ignored lookup is for authorized joins only. The suggested actions remain unvalidated until an editor reviews them.

**Credit.** [Built on the FlyRank ML Internship dataset](https://flyrank.ai). AI assisted code and drafting; the intern must verify and own the analysis before submission.
