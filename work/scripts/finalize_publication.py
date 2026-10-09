"""Record actual deployment and remove stale publication-pending wording.

Requires verified native deployment metadata in work/site/publication.json.
Does not regenerate notebook code or fabricate execution outputs.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
record = json.loads((ROOT / "work/site/publication.json").read_text(encoding="utf-8"))
assert record["status"] == "succeeded" and record["paper_url"].startswith("https://")
url = record["paper_url"]
repo = "https://github.com/Hamza2-2/flyrank-ai-internship"
(ROOT / "submission/paper_url.txt").write_text(url + "\n", encoding="utf-8")

def replace(path, replacements):
    text = path.read_text(encoding="utf-8")
    text = text.replace("https://hamza-afzal-flyrank-research.chirpy-vine-4912.chatgpt.site", url)
    for old, new in replacements:
        text = text.replace(old,new)
    path.write_text(text,encoding="utf-8")

replace(ROOT / "work/capstone_report.md", [
    ("Full-release analysis, intern/editor validation, owned-repository publication and a verified deployed paper URL remain pending.",
     "The owned public repository and deployed paper are now published. Full-release analysis and intern/editor validation remain pending."),
    ("Human validation and a public repository/deployed-paper URL are separate pending requirements.",
     f"Human validation remains pending. The public [repository]({repo}) and [deployed paper]({url}) are verified; root `submission/paper_url.txt` records the direct paper URL."),
    ("Put the verified direct paper URL, exactly one line, in `submission/paper_url.txt` only after publication, and submit the owned repository URL.",
     "Submit the owned repository URL on the portal card after personal review. No portal submission is claimed.")])

replace(ROOT / "work/assignments/ML-02_Research_Question_and_Provisional_Lane/README.md", [
    ("Hamza must validate the framing, commit to his owned public repository and submit its URL; those external requirements are pending.",
     f"The executed notebook is published in [Hamza's owned public repository]({repo}). Hamza must validate the framing and submit that URL on the portal card.")])
replace(ROOT / "work/capstones/ML_Google_Search_Ranking_and_Discoverability/README.md", [
    ("The strict attached brief's full-warehouse analysis, first-20 human content review, owned public repository, verified deployed paper and submission remain pending. None is represented as already done.",
     f"The [owned public repository]({repo}) and [deployed paper]({url}) are verified. The strict attached brief's full-warehouse analysis, first-20 human content review and portal submission remain pending.")])

# Update the saved markdown only; keep code and genuine execution records intact.
path = ROOT / "work/notebooks/capstone.ipynb"
nb = json.loads(path.read_text(encoding="utf-8"))
for cell in nb["cells"]:
    if cell["cell_type"] != "markdown":
        continue
    src = "".join(cell["source"])
    src = src.replace("https://hamza-afzal-flyrank-research.chirpy-vine-4912.chatgpt.site", url)
    src = src.replace("Full warehouse analysis, intern validation and public submission are pending.",
                      "Full warehouse analysis, intern validation and portal submission are pending. The public source repository and deployed paper are verified.")
    src = src.replace("The public repository link and `submission/paper_url.txt` must be finalized only after deployment.",
                      f"The verified [public repository]({repo}) and [paper]({url}) are recorded in the root submission metadata.")
    src = src.replace("- [ ] Owned public repo and deployed paper URL verified and submitted.",
                      "- [x] Owned public repo and deployed paper URL verified.\n- [ ] Portal submission by Hamza after personal review.")
    cell["source"] = src.splitlines(keepends=True)
path.write_text(json.dumps(nb,ensure_ascii=False,indent=1)+"\n",encoding="utf-8")

# Record the byte-preserving relocation followed by the inherited badge-only rewrite.
path = ROOT / "work/templates/relocation_receipt.json"
receipts = json.loads(path.read_text(encoding="utf-8"))
for item in receipts:
    item["sha256_at_relocation"] = item.pop("sha256",item.get("sha256_at_relocation"))
    item["sha256_current"] = hashlib.sha256((ROOT/item["preserved"]).read_bytes()).hexdigest()
    item["post_relocation_change"] = "Inherited GitHub personalize workflow changed only the Colab badge repository target."
path.write_text(json.dumps(receipts,indent=2)+"\n",encoding="utf-8")
replace(ROOT / "work/README.md",[("Eight unassigned curriculum skeletons are preserved byte-for-byte", "Eight unassigned curriculum skeletons were relocated unchanged, then had only their Colab badges personalized")])
replace(ROOT / "work/SUBMISSION_INDEX.md",[("with byte-preservation receipts", "with relocation and badge-personalization hash receipts")])
print("Recorded the verified direct paper URL and updated publication status")
