# ML-01 — Run the Starter Notebooks

Both required notebooks were executed top to bottom locally on the official public starter data. Their outputs are saved at the canonical paths:

- [01 — First look and discovery](../../../notebooks/01_first_look_and_discovery.ipynb): the full unchanged reference pipeline ran; the your-turn cell compares keyword-volume/visibility correlations with and without zero-impression pages.
- [02 — Your first readable model](../../../notebooks/02_your_first_readable_model.ipynb): the your-turn cell compares tree depths 2, 3, and 4 against a fixed rule on held-out clients, with training-only imputation.
- [Execution receipt](execution_summary.json) records executed cells and errors.

Notebook 01 uses a checked Python subprocess instead of a shell magic for reliable local execution. The reference scripts and input dataset remain unchanged.

## Reproduce

From the repository root, install `requirements.txt` plus `nbformat nbclient ipykernel`, register a Jupyter kernel named `flyrank`, and run `python work/scripts/run_starter_notebooks.py`. The script executes the notebooks; it does not fabricate outputs.

## Submission

Submit the public GitHub repository URL once published. A local folder, Drive link, or Colab link does not satisfy this card. Hugging Face account and gate access remain separately unverified; they were not needed for these two starter notebooks.
