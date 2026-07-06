import argparse
import datetime
import json
import sys
from pathlib import Path

from revolutionary_mlops.pipelines.train_pipeline import run_training_pipeline
from revolutionary_mlops.pipelines.validate_pipeline import run_validation_pipeline

QUALITY_THRESHOLD = 0.80


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train + validate + quality gate")
    parser.add_argument("--train-path", type=Path, default=Path("data/train.csv"))
    parser.add_argument("--test-path", type=Path, default=Path("data/test.csv"))
    parser.add_argument("--validate-path", type=Path, default=Path("data/validate.csv"))
    parser.add_argument(
        "--output", type=Path, default=Path("artifacts/latest_run.json")
    )
    parser.add_argument("--history", type=Path, default=Path("history/runs.jsonl"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    model_id = run_training_pipeline(
        train_path=args.train_path, test_path=args.test_path
    )
    metrics = run_validation_pipeline(
        model_id=model_id, validate_path=args.validate_path
    )

    passed = (
        metrics["accuracy"] >= QUALITY_THRESHOLD
        and metrics["precision"] >= QUALITY_THRESHOLD
        and metrics["recall"] >= QUALITY_THRESHOLD
    )

    run_record = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "model_id": model_id,
        "threshold": QUALITY_THRESHOLD,
        "passed": passed,
        **metrics,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(run_record, indent=2))

    args.history.parent.mkdir(parents=True, exist_ok=True)
    with args.history.open("a") as f:
        f.write(json.dumps(run_record) + "\n")

    print(
        f"quality_gate={'PASSED' if passed else 'FAILED'} (threshold={QUALITY_THRESHOLD})"
    )

    if not passed:
        sys.exit(1)


if __name__ == "__main__":
    main()
