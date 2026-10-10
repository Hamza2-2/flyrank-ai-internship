"""Run and save the genuine warehouse notebook after private local sign-in.

Default: preflight only. --run enables gated stages and executes every cell.
No tokens or warehouse cache rows are printed or copied into public outputs.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from huggingface_hub import get_token
from jupyter_client.kernelspec import KernelSpecManager
import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "work/templates/notebooks/warehouse_extension.ipynb"
TARGET = ROOT / "work/notebooks/warehouse_extension.ipynb"
CACHE = ROOT / "work/outputs/warehouse_cache"
OUT = ROOT / "work/outputs"


class HandoffError(RuntimeError):
    """A credential-free diagnostic written by this runner."""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true", help="Enable gated stages and execute the notebook.")
    args = parser.parse_args()
    spec = KernelSpecManager().get_kernel_spec("flyrank")
    if Path(spec.argv[0]).resolve() != Path(sys.executable).resolve():
        raise HandoffError("The flyrank kernel uses another Python environment. Register this workspace's .venv kernel first.")
    notebook = nbformat.read(TEMPLATE, as_version=4)
    nbformat.validate(notebook)
    switches = sum("RUN_GATED_STAGES = False" in cell.source for cell in notebook.cells if cell.cell_type == "code")
    if switches != 1:
        raise HandoffError("Expected exactly one gated-stage switch in the template.")
    signed_in = bool(get_token())
    print(f"Notebook template valid; correct local kernel; local HF login present: {signed_in}", flush=True)
    if not args.run:
        print("Preflight only. After accepting the dataset gate and signing in locally, run this command with --run.")
        return
    if not signed_in:
        raise HandoffError("Local HF login is unavailable. Run .venv\\Scripts\\hf.exe auth login privately first.")
    if (OUT / "warehouse_frozen_contract.json").exists() and not (CACHE / "frozen_models.joblib").exists():
        raise HandoffError("Published freeze receipts exist without the private model. Use the isolated replay instructions in warehouse_execution.md.")
    for cell in notebook.cells:
        if cell.cell_type == "code":
            cell.source = cell.source.replace("RUN_GATED_STAGES = False", "RUN_GATED_STAGES = True")
            cell.execution_count = None
            cell.outputs = []
    client = NotebookClient(notebook, kernel_name="flyrank", timeout=7200,
                            resources={"metadata": {"path": str(ROOT)}})

    def progress(cell, cell_index, **kwargs):
        if cell.cell_type == "code":
            print(f"Executing code cell at notebook position {cell_index + 1}...", flush=True)

    client.on_cell_start = progress
    client.execute()
    cells = [cell for cell in notebook.cells if cell.cell_type == "code"]
    if not all(cell.execution_count is not None for cell in cells):
        raise HandoffError("A code cell did not execute; no deliverable saved.")
    if any(output.output_type == "error" for cell in cells for output in cell.outputs):
        raise HandoffError("A cell has an error; no deliverable saved.")
    metrics_path = OUT / "warehouse_metrics.json"
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    if metrics.get("status") != "completed actual gated execution":
        raise HandoffError("No verified warehouse result exists; no deliverable saved.")
    sys.path.insert(0, str(ROOT / "work/scripts"))
    import warehouse_extension as warehouse
    if metrics.get("source_code_sha256") != warehouse.digest(ROOT / "work/scripts/warehouse_extension.py"):
        raise HandoffError("Executed result and current warehouse source differ; no deliverable saved.")
    if metrics.get("policy_sha256") != warehouse.contract_hash():
        raise HandoffError("Executed result and current contract differ; no deliverable saved.")
    nbformat.validate(notebook)
    nbformat.write(notebook, TARGET)
    print(f"Saved {TARGET.relative_to(ROOT)}: {len(cells)}/{len(cells)} code cells, zero errors, verified gated result.")
    print("Next: review outcomes/recommendations and integrate the genuine warehouse findings into the paper before portal submission.")


if __name__ == "__main__":
    try:
        main()
    except HandoffError as exc:
        print(f"STOPPED: {exc}", file=sys.stderr)
        raise SystemExit(2) from None
    except Exception:
        print("STOPPED: preflight or execution did not pass. No new executed notebook was saved. Check the kernel, private login, stage receipts and execution guide; private exception details are suppressed.", file=sys.stderr)
        raise SystemExit(2) from None
