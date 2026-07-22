#!/usr/bin/env python3
"""Validate W&B exports and build canonical historical evidence outputs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "evidence" / "alfworld_20250328"
SOURCE_DIR = EVIDENCE_DIR / "source"
DERIVED_DIR = EVIDENCE_DIR / "derived"
MANIFEST_PATH = EVIDENCE_DIR / "manifest.json"
SUMMARY_PATH = DERIVED_DIR / "summary.json"
RESULTS_PATH = DERIVED_DIR / "game_results.csv"
CHECKSUMS_PATH = EVIDENCE_DIR / "SHA256SUMS"
RUN_PREFIX = "golden-pyramid-593 - "


@dataclass(frozen=True)
class Export:
    metric: str
    rows: list[dict[str, str]]
    path: Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def read_export(path: Path, expected_metric: str) -> Export:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"Empty export: {path}")

    value_column = RUN_PREFIX + expected_metric
    minimum_column = value_column + "__MIN"
    maximum_column = value_column + "__MAX"
    missing = {value_column, minimum_column, maximum_column} - rows[0].keys()
    if missing:
        raise ValueError(f"{path.name} is missing columns: {sorted(missing)}")
    if any(
        row[value_column] != row[minimum_column]
        or row[value_column] != row[maximum_column]
        for row in rows
    ):
        raise ValueError(
            f"{path.name} contains aggregated rather than single-run values"
        )
    return Export(metric=expected_metric, rows=rows, path=path)


def load_exports(manifest: dict) -> dict[str, Export]:
    exports: dict[str, Export] = {}
    for source in manifest["sources"]:
        path = SOURCE_DIR / source["file"]
        if not path.is_file():
            raise FileNotFoundError(f"Missing source export: {path}")
        actual_hash = sha256(path)
        if actual_hash != source["sha256"]:
            raise ValueError(
                f"Hash mismatch for {path.name}: {actual_hash} != {source['sha256']}"
            )
        export = read_export(path, source["metric"])
        if export.metric in exports:
            raise ValueError(f"Duplicate metric export: {export.metric}")
        exports[export.metric] = export
    return exports


def row_ids(export: Export) -> list[int]:
    key = "game_no" if "game_no" in export.rows[0] else "Step"
    return [int(row[key]) for row in export.rows]


def validate_and_derive(
    manifest: dict, exports: dict[str, Export]
) -> tuple[list, dict]:
    required = {
        "success",
        "runtime",
        "actions_taken",
        "avg_actions_taken_per_successful_game",
        "success_rate",
    }
    if exports.keys() != required:
        raise ValueError(f"Unexpected metric set: {sorted(exports)}")

    expected_ids = list(range(1, manifest["evaluation"]["games_evaluated"] + 1))
    for export in exports.values():
        if row_ids(export) != expected_ids:
            raise ValueError(f"Non-contiguous game/step IDs in {export.path.name}")

    success_column = RUN_PREFIX + "success"
    actions_column = RUN_PREFIX + "actions_taken"
    runtime_column = RUN_PREFIX + "runtime"
    rate_column = RUN_PREFIX + "success_rate"
    average_column = RUN_PREFIX + "avg_actions_taken_per_successful_game"

    successes = [int(float(row[success_column])) for row in exports["success"].rows]
    actions = [int(float(row[actions_column])) for row in exports["actions_taken"].rows]
    runtimes = [float(row[runtime_column]) for row in exports["runtime"].rows]
    rates = [float(row[rate_column]) for row in exports["success_rate"].rows]
    averages = [
        float(row[average_column])
        for row in exports["avg_actions_taken_per_successful_game"].rows
    ]

    if any(value not in {0, 1} for value in successes):
        raise ValueError("Success export must contain only zero or one")

    derived_rows = []
    success_count = 0
    successful_actions = 0
    for game_no, success, action_count, runtime, rate, average in zip(
        expected_ids, successes, actions, runtimes, rates, averages, strict=True
    ):
        success_count += success
        if success:
            successful_actions += action_count
        expected_rate = success_count / game_no
        expected_average = successful_actions / success_count
        if not math.isclose(rate, expected_rate, rel_tol=0, abs_tol=1e-15):
            raise ValueError(f"Success-rate recurrence failed at game {game_no}")
        if not math.isclose(average, expected_average, rel_tol=0, abs_tol=1e-12):
            raise ValueError(f"Successful-action average failed at game {game_no}")
        derived_rows.append(
            {
                "game_no": game_no,
                "success": success,
                "actions_taken": action_count,
                "runtime_seconds": format(runtime, ".15g"),
                "cumulative_success_rate": format(rate, ".17g"),
                "avg_actions_per_successful_game": format(average, ".17g"),
            }
        )

    evaluation = manifest["evaluation"]
    failure_ids = [
        game_no
        for game_no, success in zip(expected_ids, successes, strict=True)
        if not success
    ]
    summary = {
        "evidence_id": manifest["evidence_id"],
        "wandb_run_id": manifest["wandb"]["run_id"],
        "wandb_display_name": manifest["wandb"]["display_name"],
        "configured_dataset": evaluation["configured_dataset"],
        "games_evaluated": len(successes),
        "successes": success_count,
        "failures": len(successes) - success_count,
        "failure_game_ids": failure_ids,
        "success_rate": success_count / len(successes),
        "successful_action_total": successful_actions,
        "avg_actions_per_successful_game": successful_actions / success_count,
        "all_action_total": sum(actions),
        "runtime_total_seconds": sum(runtimes),
        "runtime_total_hours": sum(runtimes) / 3600,
        "source_sha256": {
            source["file"]: source["sha256"] for source in manifest["sources"]
        },
    }

    expected = {
        "games_evaluated": evaluation["games_evaluated"],
        "successes": evaluation["successes"],
        "failures": evaluation["failures"],
        "success_rate": evaluation["success_rate"],
    }
    for key, value in expected.items():
        actual = summary[key]
        if isinstance(value, float):
            matches = math.isclose(actual, value, rel_tol=0, abs_tol=1e-15)
        else:
            matches = actual == value
        if not matches:
            raise ValueError(
                f"Manifest expectation failed for {key}: {actual} != {value}"
            )
    return derived_rows, summary


def csv_bytes(rows: list[dict]) -> bytes:
    buffer = io.StringIO(newline="")
    fieldnames = [
        "game_no",
        "success",
        "actions_taken",
        "runtime_seconds",
        "cumulative_success_rate",
        "avg_actions_per_successful_game",
    ]
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def json_bytes(value: dict) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def checksum_bytes(manifest: dict) -> bytes:
    lines = [
        f"{source['sha256']}  source/{source['file']}"
        for source in sorted(manifest["sources"], key=lambda item: item["file"])
    ]
    return ("\n".join(lines) + "\n").encode("utf-8")


def materialize(path: Path, content: bytes, *, check: bool) -> None:
    if check:
        if not path.is_file():
            raise FileNotFoundError(f"Missing generated output: {path}")
        if path.read_bytes() != content:
            raise ValueError(f"Generated output is stale: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def build(*, check: bool) -> dict:
    manifest = read_manifest()
    exports = load_exports(manifest)
    rows, summary = validate_and_derive(manifest, exports)
    materialize(RESULTS_PATH, csv_bytes(rows), check=check)
    materialize(SUMMARY_PATH, json_bytes(summary), check=check)
    materialize(CHECKSUMS_PATH, checksum_bytes(manifest), check=check)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="Fail if generated outputs are stale"
    )
    args = parser.parse_args()
    summary = build(check=args.check)
    verb = "Verified" if args.check else "Generated"
    print(
        f"{verb} historical evidence: {summary['successes']}/"
        f"{summary['games_evaluated']} = {summary['success_rate']:.2%}"
    )


if __name__ == "__main__":
    main()
