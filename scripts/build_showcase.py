#!/usr/bin/env python3
"""Build and verify the local, self-contained CogAgentLab showcase."""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path

from build_historical_evidence import build as build_evidence

ROOT = Path(__file__).resolve().parents[1]
SITE_DIR = ROOT / "site"
DIST_DIR = SITE_DIR / "dist"
EVIDENCE_DIR = ROOT / "evidence" / "alfworld_20250328"
SUMMARY_PATH = EVIDENCE_DIR / "derived" / "summary.json"
RESULTS_PATH = EVIDENCE_DIR / "derived" / "game_results.csv"
MANIFEST_PATH = EVIDENCE_DIR / "manifest.json"


class LinkCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag not in {"a", "link"}:
            return
        values = dict(attrs)
        key = "href"
        if values.get(key):
            self.links.append(values[key] or "")


def read_results() -> list[dict[str, str]]:
    with RESULTS_PATH.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def chart_svg(rows: list[dict[str, str]]) -> str:
    width, height = 1000, 360
    left, right, top, bottom = 70, 32, 34, 62
    plot_width = width - left - right
    plot_height = height - top - bottom
    y_min, y_max = 0.8, 1.0

    def x_position(game_no: int) -> float:
        return left + ((game_no - 1) / (len(rows) - 1)) * plot_width

    def y_position(rate: float) -> float:
        return top + ((y_max - rate) / (y_max - y_min)) * plot_height

    points = [
        (
            x_position(int(row["game_no"])),
            y_position(float(row["cumulative_success_rate"])),
        )
        for row in rows
    ]
    path = " ".join(
        f"{'M' if index == 0 else 'L'} {x:.2f} {y:.2f}"
        for index, (x, y) in enumerate(points)
    )
    failures = [
        x_position(int(row["game_no"])) for row in rows if row["success"] == "0"
    ]
    final_x, final_y = points[-1]
    grid = []
    for rate in (0.8, 0.85, 0.9, 0.95, 1.0):
        y = y_position(rate)
        grid.append(
            f'<line x1="{left}" y1="{y:.2f}" x2="{width - right}" '
            f'y2="{y:.2f}" class="chart-grid" />'
        )
        grid.append(
            f'<text x="{left - 12}" y="{y + 5:.2f}" text-anchor="end" '
            f'class="chart-label">{rate:.0%}</text>'
        )
    x_labels = []
    for game_no in (1, 35, 70, 105, 139):
        x = x_position(game_no)
        x_labels.append(
            f'<text x="{x:.2f}" y="{height - 18}" text-anchor="middle" '
            f'class="chart-label">{game_no}</text>'
        )
    failure_marks = "".join(
        f'<line x1="{x:.2f}" y1="{height - bottom + 8}" x2="{x:.2f}" '
        f'y2="{height - bottom + 19}" class="failure-mark" />'
        for x in failures
    )
    return f"""<svg viewBox="0 0 {width} {height}" role="img"
            aria-labelledby="success-chart-title success-chart-description">
          <title id="success-chart-title">Cumulative ALFWorld valid_seen task success</title>
          <desc id="success-chart-description">
            A cumulative success-rate line across 139 games, ending at 87.05 percent.
            Eighteen failure marks appear below the chart.
          </desc>
          <style>
            .chart-grid {{ stroke: #d6d4c8; stroke-width: 1; }}
            .chart-label {{ fill: #5d6963; font: 13px Inter, sans-serif; }}
            .chart-axis-title {{ fill: #17211d; font: 700 14px Inter, sans-serif; }}
            .chart-line {{ fill: none; stroke: #1c7658; stroke-width: 4; stroke-linejoin: round; }}
            .chart-end {{ fill: #1c7658; stroke: #fffdf8; stroke-width: 4; }}
            .chart-callout {{ fill: #123f35; font: 800 17px Inter, sans-serif; }}
            .failure-mark {{ stroke: #a86417; stroke-width: 3; }}
          </style>
          {"".join(grid)}
          <line x1="{left}" y1="{height - bottom}" x2="{width - right}"
            y2="{height - bottom}" stroke="#78827d" />
          <path d="{path}" class="chart-line" />
          {failure_marks}
          <circle cx="{final_x:.2f}" cy="{final_y:.2f}" r="7" class="chart-end" />
          <text x="{final_x - 12:.2f}" y="{final_y - 14:.2f}" text-anchor="end"
            class="chart-callout">121 / 139 · 87.05%</text>
          {"".join(x_labels)}
          <text x="{left + plot_width / 2:.2f}" y="{height - 1}" text-anchor="middle"
            class="chart-axis-title">Evaluated game</text>
        </svg>"""


def render_index(summary: dict, manifest: dict, rows: list[dict[str, str]]) -> bytes:
    template = (SITE_DIR / "index.html").read_text(encoding="utf-8")
    values = {
        "{{SUCCESS_RATE_PERCENT}}": f"{summary['success_rate'] * 100:.2f}",
        "{{SUCCESS_COUNT}}": str(summary["successes"]),
        "{{GAME_COUNT}}": str(summary["games_evaluated"]),
        "{{FAILURE_COUNT}}": str(summary["failures"]),
        "{{AVG_ACTIONS}}": f"{summary['avg_actions_per_successful_game']:.2f}",
        "{{RUNTIME_HOURS}}": f"{summary['runtime_total_hours']:.1f}",
        "{{FAILURE_IDS}}": ", ".join(map(str, summary["failure_game_ids"])),
        "{{CHART_SVG}}": chart_svg(rows),
        "{{EXPORT_DATE}}": html.escape(manifest["exported_at"]),
    }
    for marker, value in values.items():
        template = template.replace(marker, value)
    unresolved = sorted(set(re.findall(r"\{\{[A-Z_]+\}\}", template)))
    if unresolved:
        raise ValueError(f"Unresolved site template markers: {unresolved}")
    return template.encode("utf-8")


def expected_outputs(summary: dict) -> dict[Path, bytes]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    rows = read_results()
    outputs = {
        DIST_DIR / "index.html": render_index(summary, manifest, rows),
        DIST_DIR / "styles.css": (SITE_DIR / "styles.css").read_bytes(),
        DIST_DIR / "evidence" / "game_results.csv": RESULTS_PATH.read_bytes(),
        DIST_DIR / "evidence" / "summary.json": SUMMARY_PATH.read_bytes(),
        DIST_DIR / "evidence" / "manifest.json": MANIFEST_PATH.read_bytes(),
        DIST_DIR / "evidence" / "SHA256SUMS": (
            EVIDENCE_DIR / "SHA256SUMS"
        ).read_bytes(),
        DIST_DIR / "evidence" / "README.md": (EVIDENCE_DIR / "README.md").read_bytes(),
    }
    for source in manifest["sources"]:
        filename = source["file"]
        outputs[DIST_DIR / "evidence" / "source" / filename] = (
            EVIDENCE_DIR / "source" / filename
        ).read_bytes()
    return outputs


def materialize(outputs: dict[Path, bytes], *, check: bool) -> None:
    for path, content in outputs.items():
        if check:
            if not path.is_file():
                raise FileNotFoundError(f"Missing generated site file: {path}")
            if path.read_bytes() != content:
                raise ValueError(f"Generated site file is stale: {path}")
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)


def check_links(index: bytes, outputs: dict[Path, bytes]) -> None:
    parser = LinkCollector()
    parser.feed(index.decode("utf-8"))
    expected_paths = {path.resolve() for path in outputs}
    for link in parser.links:
        if link.startswith(("#", "http://", "https://", "mailto:")):
            continue
        target = (DIST_DIR / link.split("#", 1)[0]).resolve()
        if target not in expected_paths:
            raise ValueError(f"Broken bundled link: {link}")


def check_privacy(outputs: dict[Path, bytes]) -> None:
    forbidden = {
        "home path": re.compile(rb"/home/[A-Za-z0-9._-]+"),
        "workspace path": re.compile(rb"/workspace/"),
        "secret token": re.compile(
            rb"(?:sk-[A-Za-z0-9_-]{16,}|AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{20,})"
        ),
    }
    for path, content in outputs.items():
        for label, pattern in forbidden.items():
            if pattern.search(content):
                raise ValueError(f"Public bundle contains {label}: {path}")


def build(*, check: bool) -> None:
    summary = build_evidence(check=check)
    outputs = expected_outputs(summary)
    index = outputs[DIST_DIR / "index.html"]
    check_links(index, outputs)
    check_privacy(outputs)
    materialize(outputs, check=check)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="Fail if the bundled preview is stale"
    )
    args = parser.parse_args()
    build(check=args.check)
    verb = "Verified" if args.check else "Built"
    print(f"{verb} self-contained showcase: {DIST_DIR}")


if __name__ == "__main__":
    main()
