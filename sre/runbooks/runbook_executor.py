"""
helios/sre/runbooks/runbook_executor.py
───────────────────────────────────────
YAML-driven automated runbook executor.
Loads a runbook definition, executes each step in order, and
posts a summary to Slack. Designed to be triggered by alerts
from the Helios alerting engine.

Usage:
    python runbook_executor.py --runbook runbooks/high_latency.yaml
    python runbook_executor.py --runbook runbooks/error_spike.yaml --dry-run
"""

from __future__ import annotations

import argparse
import logging
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import requests
import yaml

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


# ── Data models ──────────────────────────────────────────────────────────────

StepType = Literal["shell", "http_post", "http_get", "wait", "slack"]


@dataclass
class Step:
    name: str
    type: StepType
    command: str | None = None      # shell
    url: str | None = None          # http_*
    body: dict | None = None        # http_post
    seconds: int = 0                # wait
    message: str | None = None      # slack
    continue_on_failure: bool = False


@dataclass
class Runbook:
    name: str
    description: str
    severity: str
    steps: list[Step]
    notify_slack_on_failure: bool = True


@dataclass
class ExecutionReport:
    runbook_name: str
    total_steps: int
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    duration_s: float = 0.0
    step_results: list[dict] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return self.failed == 0


# ── Parsing ───────────────────────────────────────────────────────────────────

def load_runbook(path: Path) -> Runbook:
    data = yaml.safe_load(path.read_text())
    steps = [Step(**s) for s in data.get("steps", [])]
    return Runbook(
        name=data["name"],
        description=data.get("description", ""),
        severity=data.get("severity", "unknown"),
        steps=steps,
        notify_slack_on_failure=data.get("notify_slack_on_failure", True),
    )


# ── Step executors ────────────────────────────────────────────────────────────

def run_shell(step: Step, dry_run: bool) -> bool:
    log.info("  [shell] %s", step.command)
    if dry_run:
        log.info("  [dry-run] skipping shell execution")
        return True
    result = subprocess.run(step.command, shell=True, capture_output=True, text=True, timeout=60)
    if result.stdout:
        log.info("  stdout: %s", result.stdout.strip())
    if result.stderr:
        log.warning("  stderr: %s", result.stderr.strip())
    return result.returncode == 0


def run_http(step: Step, dry_run: bool) -> bool:
    log.info("  [%s] %s", step.type, step.url)
    if dry_run:
        log.info("  [dry-run] skipping HTTP call")
        return True
    try:
        if step.type == "http_post":
            resp = requests.post(step.url, json=step.body, timeout=10)
        else:
            resp = requests.get(step.url, timeout=10)
        log.info("  response: %d", resp.status_code)
        return resp.status_code < 400
    except requests.RequestException as exc:
        log.error("  HTTP error: %s", exc)
        return False


def run_wait(step: Step) -> bool:
    log.info("  [wait] %ds", step.seconds)
    time.sleep(step.seconds)
    return True


def run_slack(step: Step, dry_run: bool) -> bool:
    webhook = __import__("os").environ.get("SLACK_WEBHOOK_URL")
    if not webhook:
        log.warning("  [slack] SLACK_WEBHOOK_URL not set — skipping notification")
        return True
    if dry_run:
        log.info("  [dry-run] slack message: %s", step.message)
        return True
    try:
        resp = requests.post(webhook, json={"text": step.message}, timeout=5)
        return resp.status_code == 200
    except requests.RequestException as exc:
        log.error("  Slack error: %s", exc)
        return False


# ── Main executor ─────────────────────────────────────────────────────────────

def execute(runbook: Runbook, dry_run: bool = False) -> ExecutionReport:
    log.info("▶ Executing runbook: %s (%s)", runbook.name, runbook.severity)
    log.info("  %s", runbook.description)
    report = ExecutionReport(runbook_name=runbook.name, total_steps=len(runbook.steps))
    start = time.monotonic()

    for i, step in enumerate(runbook.steps, 1):
        log.info("Step %d/%d — %s", i, len(runbook.steps), step.name)
        try:
            if step.type == "shell":
                ok = run_shell(step, dry_run)
            elif step.type in ("http_post", "http_get"):
                ok = run_http(step, dry_run)
            elif step.type == "wait":
                ok = run_wait(step)
            elif step.type == "slack":
                ok = run_slack(step, dry_run)
            else:
                log.error("  Unknown step type: %s", step.type)
                ok = False
        except Exception as exc:
            log.error("  Unexpected error in step '%s': %s", step.name, exc)
            ok = False

        status = "✓ passed" if ok else "✗ failed"
        log.info("  → %s", status)
        report.step_results.append({"step": step.name, "ok": ok})

        if ok:
            report.passed += 1
        else:
            report.failed += 1
            if not step.continue_on_failure:
                log.error("Aborting runbook — step '%s' failed", step.name)
                report.skipped = len(runbook.steps) - i
                break

    report.duration_s = time.monotonic() - start
    log.info(
        "Runbook complete in %.1fs — passed=%d failed=%d skipped=%d",
        report.duration_s, report.passed, report.failed, report.skipped,
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Helios runbook executor")
    parser.add_argument("--runbook",  required=True, type=Path)
    parser.add_argument("--dry-run",  action="store_true")
    args = parser.parse_args()

    runbook = load_runbook(args.runbook)
    report = execute(runbook, dry_run=args.dry_run)
    sys.exit(0 if report.success else 1)


if __name__ == "__main__":
    main()
