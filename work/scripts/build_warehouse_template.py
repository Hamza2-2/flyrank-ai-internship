"""Author a pending warehouse template; this does not execute gated queries."""
from pathlib import Path
import nbformat as nbf

ROOT = Path(__file__).resolve().parents[2]
M = nbf.v4.new_markdown_cell
C = nbf.v4.new_code_cell


def build():
    cells = [
        C("%pip install -q duckdb huggingface_hub pandas scikit-learn matplotlib"),
        M("# Warehouse extension — pending authenticated execution\n\nThis is a new extension template, separate from the original eight relocated assignment skeletons. The published starter capstone remains unchanged. This template defaults to offline plan/synthetic checks and does not claim warehouse results. After all gated stages genuinely pass, save a copy with visible outputs to `work/notebooks/warehouse_extension.ipynb`.\n\nRead [the execution guide](../../capstones/ML_Google_Search_Ranking_and_Discoverability/warehouse_execution.md) before enabling remote stages. No token belongs in a cell or command argument."),
        C('''from pathlib import Path
import sys, subprocess, json
candidate = Path.cwd().resolve()
ROOT = next((path for path in [candidate, *candidate.parents]
             if (path / "work/scripts/warehouse_extension.py").exists()), None)
if ROOT is None:
    checkout = candidate / "flyrank-ai-internship"
    if not checkout.exists():
        subprocess.run(["git", "clone", "--depth", "1", "https://github.com/Hamza2-2/flyrank-ai-internship", str(checkout)],
                       check=True, capture_output=True, text=True)
    ROOT = checkout.resolve()
    if not (ROOT / "work/scripts/warehouse_extension.py").exists():
        raise FileNotFoundError("The public checkout does not contain the prepared extension yet.")
sys.path.insert(0, str(ROOT / "work/scripts"))
import warehouse_extension as warehouse
from IPython.display import display
RUN_GATED_STAGES = False  # Change only after your local HF login and dataset gate are ready.
REPLAY_RUN = ""
if (warehouse.OUT / "warehouse_frozen_contract.json").exists() and not (warehouse.CACHE / "frozen_models.joblib").exists():
    REPLAY_RUN = "reproduction_01"
    warehouse.configure_replay(REPLAY_RUN)
    print("Published historical receipts detected without private cache: isolated replay, not new validation.")
print("Saved local authentication available:", warehouse.token_available())
print("Remote stages enabled:", RUN_GATED_STAGES)

def run_stage(name):
    if name not in {"plan", "self-check"} and not RUN_GATED_STAGES:
        print(f"PENDING: {name} not executed; authenticated extension remains a template.")
        return
    command = [sys.executable, str(ROOT / "work/scripts/warehouse_extension.py"), "--stage", name]
    if REPLAY_RUN:
        command += ["--replay", REPLAY_RUN]
    result = subprocess.run(command,
                            cwd=str(ROOT), capture_output=True, text=True)
    print(result.stdout)
    if result.returncode:
        raise RuntimeError(f"Stage {name} did not pass. Credential-bearing stderr is suppressed; inspect the sanitized stdout and execution guide.")
'''),
        M("## Predeclared decision and data contract\n\nThe editor chooses which pages to inspect first. For decision midnight June 1, features use [D−90 days,D), the reference uses [D−30 days,D), and the future outcome uses June 1–30. The observed daily-rate ratio defines decline; editorial usefulness and causal benefit remain unmeasured. Feature/label/eligibility/model choices are frozen before June access, and clients are disjoint across earlier training, April validation and June test. Current content snapshots and fixed-90-day query facts are excluded."),
        C("run_stage('plan')"),
        M("## Offline integrity verification\n\nThe next cell uses generated synthetic rows only. It checks exact half-open windows, future perturbation invariance, tracking unavailability versus observed zero, and duplicate detection. Passing it is implementation verification, not warehouse evidence."),
        C("run_stage('self-check')"),
        M("## Authenticate and inspect actual schema\n\nUse your local Hugging Face sign-in/read token and accepted gate; the script calls `get_token()` privately. Required fields and semantics must pass actual March schema, grain, null-key, finite-metric and client-dimension audits. No assumptions are adapted silently."),
        C("run_stage('inspect')"),
        M("## Develop on March; keep June sealed\n\nThis verifies the aggregate query on the mid-panel month. It is not a model evaluation and never falls back to the final-month sample."),
        C("run_stage('develop')"),
        M("## Cache prior-only study windows\n\nThe script reads/project-aggregates the non-June release partitions and writes local page-at-decision features. All raw daily rows remain outside pandas. Private artifacts under `work/outputs/warehouse_cache/` stay ignored by git. Existing passed caches are reviewed/reused by starting from the next stage, rather than rescanned."),
        C("run_stage('aggregate')"),
        M("## Freeze development selection before June\n\nA new historical-momentum/visibility/position rule competes with two fixed models on identical April validation clients. June test clients are absent from fitting. Public contract hashes bind code, policy, client/feature cache and model artifact; public outputs show counts, never actual client/content hashes. Selection/exclusion counts and undefined labels are reported."),
        C("run_stage('freeze')"),
        M("## Evaluate the sealed June outcome once\n\nOnly a matching freeze permits this stage. A private access marker is written before the first June query and prevents refreezing. Missing/untracked outcomes are undefined; observed zero impressions are valid. Final metrics compare methods on the same adequately observed subset; recommendations include all prior-eligible candidates and do not use future labels as inputs."),
        C("run_stage('evaluate')"),
        M("## Read genuine public evidence\n\nThese artifacts exist only after their stages successfully execute. Absence is a pending requirement, not a zero-valued result. The starter JSON and report remain separate."),
        C('''for name in ["warehouse_schema_audit.json", "warehouse_development_receipt.json",
             "warehouse_aggregation_receipt.json", "warehouse_frozen_contract.json", "warehouse_metrics.json"]:
    path = warehouse.OUT / name
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        print(name, "status:", data.get("status"))
        if name == "warehouse_metrics.json":
            display(data["test_metrics"])
            display(data["eligibility"])
    else:
        print(name, "PENDING: no completed execution receipt")
'''),
        M("## Completion conditions and credit\n\n- Actual schema, grain, quality and join audits pass.\n- All gated stages execute with original frozen plan/model and June access record preserved.\n- The saved canonical notebook contains genuine outputs, and no private cache is published.\n- Intern/editor review checks the result, first 20 cases and scope limitations before paper integration.\n- Actual internship portal submission is a personal step.\n\n[Built on the FlyRank ML Internship dataset](https://flyrank.ai). This prepared template must not be presented as a completed warehouse experiment."),
    ]
    nb = nbf.v4.new_notebook(cells=cells)
    nb.metadata["kernelspec"] = {"display_name":"Python 3 (FlyRank)","name":"flyrank","language":"python"}
    nb.metadata["language_info"] = {"name":"python","version":"3.11"}
    path = ROOT / "work/templates/notebooks/warehouse_extension.ipynb"
    path.parent.mkdir(parents=True,exist_ok=True)
    nbf.write(nb,str(path))
    print("New pending extension template authored; no gated queries executed.")


if __name__=="__main__": build()
