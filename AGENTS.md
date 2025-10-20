# Repository Guidelines

## Project Structure & Module Organization
Core Earth Engine logic lives in `modules/`, powering dataset registration, risk scoring, and utilities shared by notebooks and the API. Dataset lookup CSVs sit in `parameters/`; edit them whenever you add or rename layers. The FastAPI service is under `api/app` with compose scripts beside it, while bulk notebooks (e.g., `whisp_feature_collection.ipynb`) remain in the root. Sample inputs are in `input_examples/`, and generated outputs should land in `results/`.

## Build, Test, and Development Commands
Python 3.10 virtual envs keep dependencies isolated:
- `cd api && python -m venv venv && source venv/bin/activate`
- `cd api && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
- `cd api && docker-compose up --build` for container checks
- `cd api && pytest` for the automated suite (requires GEE auth)
Copy `.env.example` to `.env`, set `GEE_PROJECT`, then run `earthengine authenticate`.

## Coding Style & Naming Conventions
Follow PEP 8 with four-space indentation, `snake_case` for functions and modules, `PascalCase` for classes, and clear uppercase constants. Keep docstrings concise as in `api/app/main.py`, favour f-strings for logging, and group imports as standard library, third-party, then local. Preserve existing type hints and prefer small, pure helpers around Earth Engine calls.

## Testing Guidelines
Tests use `pytest` and live in `api/tests`. Name files `test_*.py`, keep fixtures independent, and mock Earth Engine where possible. If a scenario must hit GEE, mark it `@pytest.mark.integration` and gate it behind environment or credential checks so the default `pytest` run stays deterministic. Update example payloads whenever API schemas change.

## Commit & Pull Request Guidelines
Commit messages here are short present-tense directives (`Update layers_description.md`, `Add graphics to README.md`); stick to one logical change per commit. Pull requests should summarise behaviour changes, link issues, and note any manual GEE setup reviewers need. Confirm linting and `pytest` results in the description and add screenshots when outputs change.

## Environment & Security Notes
Keep secrets out of version control: never commit `.env`, credential tokens, or raw customer data. Refresh `earthengine authenticate` regularly and scrub generated CSVs in `results/` for sensitive columns before sharing. When new datasets land, update both `modules/datasets.py` and `parameters/lookup_gee_datasets.csv` so risk calculations remain reproducible.
