"""Retarget owned-repository notebook badges without changing computed outputs."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
unassigned = ["w02_ml_task_framing", "w03_data_contract", "w03_feature_leakage_check",
              "w04_signal_audit", "w04_baseline_score", "w05_model",
              "w06_validation_audit", "w07_action_playbook"]
path = ROOT / "work/README.md"
text = path.read_text(encoding="utf-8")
for name in unassigned:
    text = text.replace("work/notebooks/" + name + ".ipynb", "work/templates/notebooks/" + name + ".ipynb")
    text = text.replace("`notebooks/" + name + ".ipynb`", "`templates/notebooks/" + name + ".ipynb`")
if "## Requested submission scope" not in text:
    text += """
## Requested submission scope

This request contains ML-01, ML-02 and the ML capstone, plus the separate AI Fluency tasks. Eight unassigned curriculum skeletons are preserved byte-for-byte in `templates/notebooks/`; `templates/relocation_receipt.json` records their checksums. They are resources for future work. Active `notebooks/` contains the executed requested ML-02 and capstone deliverables. See `SUBMISSION_INDEX.md` for all eight task folders.
"""
path.write_text(text, encoding="utf-8")
paths = list(ROOT.glob("*.md")) + list((ROOT / "work").rglob("*.md"))
paths += list((ROOT / "notebooks").glob("*.ipynb")) + list((ROOT / "work/notebooks").glob("*.ipynb"))
# Unassigned templates remain byte-for-byte intact, including original badges.
for path in paths:
    if ".git" in path.parts:
        continue
    text = path.read_text(encoding="utf-8")
    changed = text.replace("colab.research.google.com/github/flyrank-bih/flyrank-ml-internship-starter",
                           "colab.research.google.com/github/Hamza2-2/flyrank-ai-internship")
    if changed != text:
        path.write_text(changed, encoding="utf-8")
print("Owned-repository Colab badges and template index updated")
