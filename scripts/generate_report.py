

import argparse
import json
from pathlib import Path

ROW_TEMPLATE = """
<tr>
  <td>{timestamp}</td>
  <td>{model_id}</td>
  <td>{accuracy:.2%}</td>
  <td>{precision:.2%}</td>
  <td>{recall:.2%}</td>
  <td>{status}</td>
</tr>
""".strip()

PAGE_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>revolutionary-mlops — model status</title>
</head>
<body>
<h1>revolutionary-mlops — latest model status</h1>

<h2>Latest run</h2>
<ul>
  <li><strong>Model ID:</strong> {latest_model_id}</li>
  <li><strong>Timestamp (UTC):</strong> {latest_timestamp}</li>
  <li><strong>Accuracy:</strong> {latest_accuracy:.2%}</li>
  <li><strong>Precision:</strong> {latest_precision:.2%}</li>
  <li><strong>Recall:</strong> {latest_recall:.2%}</li>
  <li><strong>Quality gate:</strong> {latest_status}</li>
</ul>

<h2>Run history</h2>
<table border="1" cellpadding="4" cellspacing="0">
<thead>
<tr><th>Timestamp</th><th>Model ID</th><th>Accuracy</th><th>Precision</th><th>Recall</th><th>Status</th></tr>
</thead>
<tbody>
{rows}
</tbody>
</table>

</body>
</html>
""".strip()


def load_history(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open() as f:
        return [json.loads(line) for line in f if line.strip()]


def render(history: list[dict]) -> str:
    latest = history[-1]
    rows = "\n".join(
        ROW_TEMPLATE.format(
            timestamp=run["timestamp"],
            model_id=run["model_id"],
            accuracy=run["accuracy"],
            precision=run["precision"],
            recall=run["recall"],
            status="PASSED" if run["passed"] else "FAILED",
        )
        for run in reversed(history)
    )
    return PAGE_TEMPLATE.format(
        latest_model_id=latest["model_id"],
        latest_timestamp=latest["timestamp"],
        latest_accuracy=latest["accuracy"],
        latest_precision=latest["precision"],
        latest_recall=latest["recall"],
        latest_status="PASSED" if latest["passed"] else "FAILED",
        rows=rows,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Render model status HTML page")
    parser.add_argument("--history", type=Path, default=Path("history/runs.jsonl"))
    parser.add_argument("--output-dir", type=Path, default=Path("docs"))
    args = parser.parse_args()

    history = load_history(args.history)
    if not history:
        raise SystemExit(
            "No runs found in history file; run scripts/run_pipeline.py first"
        )

    html = render(history)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "index.html").write_text(html)
    print(f"wrote {args.output_dir / 'index.html'}")


if __name__ == "__main__":
    main()
