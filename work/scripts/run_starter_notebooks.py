"""Complete the guided experiments, execute notebooks, and save genuine outputs."""
import json
import os
from pathlib import Path
import shutil

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[2]
os.environ["PYTHONUTF8"] = "1"
OUT = ROOT / "work/assignments/ML-01_Run_the_Starter_Notebooks"
OUT.mkdir(parents=True, exist_ok=True)

first = ROOT / "notebooks/01_first_look_and_discovery.ipynb"
nb = nbformat.read(first, as_version=4)
nb.cells[4].source = "# Use a checked subprocess so a failed pipeline fails this notebook.\nsubprocess.run([sys.executable, 'scripts/run_all.py'], check=True)"
nb.cells[17].source = '''# Hamza Afzal's chosen experiment: search volume vs observed visibility.
all_corr = df["search_volume"].corr(df["impressions_90d"])
observed = df.loc[df["impressions_90d"] > 0]
visible_corr = observed["search_volume"].corr(observed["impressions_90d"])
print(f"All pages: {len(df):,}; positive-impression pages: {len(observed):,}")
print(f"Pearson correlation, all pages: {all_corr:.4f}")
print(f"Pearson correlation, positive-impression pages: {visible_corr:.4f}")
print("Observed association only: filtering pages changes the sample. These")
print("correlations do not show a causal ranking signal or forecast future clicks.")
print("I would review content-specific evidence instead of prioritizing by keyword volume alone.")
'''
nb.metadata.kernelspec = {"display_name": "Python 3", "language": "python", "name": "python3"}
nbformat.write(nb, first)

second = ROOT / "notebooks/02_your_first_readable_model.ipynb"
nb = nbformat.read(second, as_version=4)
nb.cells[16].source = '''# Honest extension: compare readable trees on entirely held-out clients.
from sklearn.model_selection import GroupShuffleSplit
from sklearn.impute import SimpleImputer
splitter = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
train_idx, test_idx = next(splitter.split(df, y, groups=df["client_id"]))
assert set(df.iloc[train_idx]["client_id"]).isdisjoint(set(df.iloc[test_idx]["client_id"]))
imputer = SimpleImputer(strategy="median", add_indicator=True)
safe_x = df[features].replace([np.inf, -np.inf], np.nan)
train_x = imputer.fit_transform(safe_x.iloc[train_idx])
test_x = imputer.transform(safe_x.iloc[test_idx])
heldout_y = y[test_idx]
print(f"Train: {len(train_idx):,} pages; test: {len(test_idx):,} pages")
print("Client overlap: 0. Imputation fitted on training data only.")
print("The held-out test is a teaching comparison; it is not a tuning dataset.")
rows = [{"method": "fixed hand rule", "precision_at_50":
         precision_at_k(df.iloc[test_idx]["hand_rule_score"], heldout_y, 50)}]
for depth in (2, 3, 4):
    candidate = DecisionTreeClassifier(max_depth=depth, class_weight="balanced", random_state=42)
    candidate.fit(train_x, y[train_idx])
    score = candidate.predict_proba(test_x)[:, 1]
    rows.append({"method": f"tree depth {depth}",
                 "precision_at_50": precision_at_k(score, heldout_y, 50)})
print(pd.DataFrame(rows).to_string(index=False))
print("Tied leaf probabilities make top-50 ordering fragile. No causal or future-outcome claim.")
'''
nb.metadata.kernelspec = {"display_name": "Python 3", "language": "python", "name": "python3"}
nbformat.write(nb, second)

summary = []
for path in (first, second):
    print(f"Executing {path.name}", flush=True)
    nb = nbformat.read(path, as_version=4)
    NotebookClient(nb, timeout=1200, kernel_name="flyrank", resources={"metadata": {"path": str(ROOT)}}).execute()
    nbformat.write(nb, path)
    code = [c for c in nb.cells if c.cell_type == "code"]
    assert all(c.execution_count is not None for c in code)
    assert not any(o.output_type == "error" for c in code for o in c.outputs)
    summary.append({"path": str(path.relative_to(ROOT)).replace("\\", "/"),
                    "code_cells": len(code), "executed_cells": len(code),
                    "cells_with_outputs": sum(bool(c.outputs) for c in code),
                    "errors": 0, "your_turn_attempted": True})
    print(f"Saved real outputs: {len(code)} code cells, zero errors", flush=True)

(OUT / "execution_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
(OUT / "README.md").write_text('''# ML-01 — Run the Starter Notebooks

Both required notebooks were executed top to bottom locally on the official public starter data. Their outputs are saved at the canonical paths:

- [01 — First look and discovery](../../../notebooks/01_first_look_and_discovery.ipynb): the full unchanged reference pipeline ran; the your-turn cell compares keyword-volume/visibility correlations with and without zero-impression pages.
- [02 — Your first readable model](../../../notebooks/02_your_first_readable_model.ipynb): the your-turn cell compares tree depths 2, 3, and 4 against a fixed rule on held-out clients, with training-only imputation.
- [Execution receipt](execution_summary.json) records executed cells and errors.

Notebook 01 uses a checked Python subprocess instead of a shell magic for reliable local execution. The reference scripts and input dataset remain unchanged.

## Reproduce

From the repository root, install `requirements.txt` plus `nbformat nbclient ipykernel`, register a Jupyter kernel named `flyrank`, and run `python work/scripts/run_starter_notebooks.py`. The script executes the notebooks; it does not fabricate outputs.

## Submission

Submit the public GitHub repository URL once published. A local folder, Drive link, or Colab link does not satisfy this card. Hugging Face account and gate access remain separately unverified; they were not needed for these two starter notebooks.
''', encoding="utf-8")
