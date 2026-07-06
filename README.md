# revolutionary-mlops

A revolutionary ML project that trains a model guaranteed to return `TRUE` for any input. Powered by cutting-edge Gaussian statistics and the world's most optimistic threshold classifier.

## Requirements

- [uv](https://github.com/astral-sh/uv)

## Setup

```bash
uv sync
```

## Running

### Train

```bash
uv run -m revolutionary_mlops train [--train-path data/train.csv] [--test-path data/test.csv]
```

Trains the model, evaluates on test data and auto-magically stores it in a secure place. Prints the `model_id` to use for validation.

### Validate

```bash
uv run -m revolutionary_mlops validate <model_id> [--validate-path data/validate.csv]
```

Retrieves the model by `model_id` and evaluates on validation data, printing accuracy/precision/recall.

### Data format

CSV files have no header. Each row starts with the target (`TRUE`) followed by a variable number of random features:

```
TRUE,0.4023,0.7235,0.3185
TRUE,0.1969,0.5479,0.6219,0.9172,0.2438,0.1050
```

## CI/CD pipeline

Every push/PR to `main` runs `.github/workflows/ci-cd.yml`, made up of chained jobs
(each one only runs if the previous one succeeded):

1. **lint** — `ruff check`, `ruff format --check` and `ty check` on all code and tests.
2. **test** — `pytest`.
3. **train-and-validate** — trains a new model version and validates it, via the
   reusable script `scripts/run_pipeline.py` (can also be run locally). It fails
   the job if accuracy, precision or recall on the validation set drop below 80%.
   On success, `scripts/generate_report.py` renders `docs/index.html` from the
   run history, which is committed back to the repo (`history/runs.jsonl`).
4. **deploy** — only runs after a successful quality gate on `main`; publishes
   `docs/` to GitHub Pages.

Run the same checks locally:

```bash
uv run ruff check .
uv run ruff format --check .
uv run ty check .
uv run pytest -q
uv run python scripts/run_pipeline.py
uv run python scripts/generate_report.py
```
