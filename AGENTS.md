# Repository Guidelines

## Project Structure & Modules
- Core loaders and workflows live in `benchmarkLoader`, `workflow`, `symDataloader`, and `symWorkflow`.
- Utility code (LLM wrappers, DB helper, Streamlit helpers) is in `benchmarkUtils`.
- Datasets, tasks, and results are under `symDataset` (e.g., `symDataset/scaledDB`, `symDataset/tasks`, `symDataset/results`).
- The Streamlit UI entrypoint is `server.py`; additional pages are under `pages/`.
- Analysis and evaluation scripts are in `symAnalysis` and `tqabench`.

## Build, Run, and Development
- Use Python 3.9+ and a virtualenv/conda env.
- Install dependencies via `pip install -r requirements.txt` (or mirror the imports from `benchmarkUtils`, `symDataloader`, etc., if no requirements file is present).
- Run the UI with `streamlit run server.py` from the repo root.
- Run analysis scripts directly, e.g. `python symAnalysis/overall.py` or `python tqabench/eval.py`, after preparing the data described in `README.md`.

## Coding Style & Naming
- Follow PEP 8: 4-space indentation, snake_case for functions/variables, PascalCase for classes.
- Keep modules small and focused; mirror existing patterns in `benchmarkLoader` and `symDataloader` when adding new datasets or workflows.
- Prefer explicit imports from project packages (e.g., `from benchmarkUtils.database import DB`) and avoid circular imports.
- Type hints are welcome but not required; when added, keep them lightweight and consistent.

## Testing & Validation
- There is no central test suite yet; prefer lightweight script-level checks.
- When adding logic, include a minimal `if __name__ == "__main__":` example or a small test script under a nearby module (e.g., see `benchmarkLoader/tableQALoader.py`).
- For more formal tests, you may add `pytest`-style tests under `tests/`, but keep them fast and focused on core loaders and workflows.

## Commits & Pull Requests
- Follow existing commit style: short, present-tense summaries (e.g., `sql eval`, `batch test finished`).
- One logical change per commit; keep diffs focused.
- For PRs, include:
  - A brief description of the change and motivation.
  - How you validated it (commands run, datasets used).
  - Any data or config assumptions (e.g., which `symDataset` subfolders are required).

## Security & Configuration
- Do not commit secrets or API keys. Streamlit credentials are loaded from `st.secrets` (e.g., `.streamlit/secrets.toml` with a `[passwords]` section); keep this file local.
- Be careful with large or private datasets under `symDataset` and `dataset/`; assume they may contain sensitive or proprietary data and avoid uploading them with code changes.

