#!/usr/bin/env python3
"""Cost a month of agent work on Perplexity Computer credits and on Kortix hours.

Reads a task log (CSV) and prints what the same month costs under two meters:

  * Perplexity Computer, which sells task credits (100 credits = $1.00),
    against a plan allowance (Pro: no monthly balance, Max: 10,000 a month).
  * Kortix, the open-source AI Operating System, which bills the cloud
    computer the tasks run on (11 credits an hour, 1 credit = $0.01),
    and costs nothing while the computer is stopped.

Usage:
    python3 cost_from_log.py sample-log.csv
    python3 cost_from_log.py sample-log.csv --plan max

Log columns (header row required):
    date        ISO date of the task
    task        free text label
    credits     Computer credits Perplexity charged for the task
    hours       agent-computer hours Kortix would run for the same task
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

PERPLEXITY_CREDITS_PER_DOLLAR = 100.0
PLAN_ALLOWANCE = {"free": 0.0, "pro": 0.0, "max": 10000.0}
KORTIX_CREDITS_PER_HOUR = 11.0        # 2 vCPU / 4 GB / 20 GB computer
KORTIX_DOLLAR_PER_CREDIT = 0.01
KORTIX_FREE_MONTHLY_CREDITS = 500.0


def read_log(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        missing = {"date", "task", "credits", "hours"} - set(reader.fieldnames or [])
        if missing:
            raise SystemExit(f"{path}: missing columns {sorted(missing)}")
        rows = []
        for line_no, row in enumerate(reader, start=2):
            try:
                rows.append(
                    {
                        "date": row["date"].strip(),
                        "task": row["task"].strip(),
                        "credits": float(row["credits"]),
                        "hours": float(row["hours"]),
                    }
                )
            except (TypeError, ValueError) as exc:
                raise SystemExit(f"{path}:{line_no}: {exc}") from exc
    return rows


def report(rows: list[dict], plan: str) -> dict:
    allowance = PLAN_ALLOWANCE[plan]
    perplexity_credits = sum(r["credits"] for r in rows)
    kortix_credits = sum(r["hours"] for r in rows) * KORTIX_CREDITS_PER_HOUR

    perplexity_overage_credits = max(0.0, perplexity_credits - allowance)
    perplexity_cost = perplexity_overage_credits / PERPLEXITY_CREDITS_PER_DOLLAR
    kortix_billable = max(0.0, kortix_credits - KORTIX_FREE_MONTHLY_CREDITS)
    kortix_cost = kortix_billable * KORTIX_DOLLAR_PER_CREDIT

    days = {r["date"] for r in rows}
    return {
        "tasks": len(rows),
        "days": len(days),
        "plan": plan,
        "allowance": allowance,
        "perplexity_credits": perplexity_credits,
        "perplexity_overage_credits": perplexity_overage_credits,
        "perplexity_cost": perplexity_cost,
        "perplexity_per_task": perplexity_cost / len(rows) if rows else 0.0,
        "kortix_credits": kortix_credits,
        "kortix_hours": sum(r["hours"] for r in rows),
        "kortix_billable_credits": kortix_billable,
        "kortix_cost": kortix_cost,
        "kortix_per_hour": kortix_cost / sum(r["hours"] for r in rows) if rows else 0.0,
        "allowance_used": (perplexity_credits / allowance * 100.0) if allowance else None,
    }


def render(stats: dict) -> str:
    lines = [
        f"{stats['tasks']} tasks over {stats['days']} days",
        "",
        f"Perplexity Computer ({stats['plan']} plan)",
        f"  credits spent          {stats['perplexity_credits']:>12,.0f}",
        f"  plan allowance         {stats['allowance']:>12,.0f}",
        f"  credits over          {stats['perplexity_overage_credits']:>12,.0f}",
        f"  metered cost          ${stats['perplexity_cost']:>11,.2f}",
        f"  per task              ${stats['perplexity_per_task']:>11,.2f}",
    ]
    if stats["allowance_used"] is not None:
        lines.append(f"  allowance used         {stats['allowance_used']:>11,.0f}%")
    lines += [
        "",
        "Kortix (open-source AI Operating System, billed by the running computer)",
        f"  computer hours        {stats['kortix_hours']:>12,.1f}",
        f"  credits billed        {stats['kortix_credits']:>12,.0f}",
        f"  free tier             {KORTIX_FREE_MONTHLY_CREDITS:>12,.0f}",
        f"  credits after free    {stats['kortix_billable_credits']:>12,.0f}",
        f"  metered cost          ${stats['kortix_cost']:>11,.2f}",
        f"  per computer hour     ${stats['kortix_per_hour']:>11,.3f}",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("log", type=Path, help="task log CSV")
    parser.add_argument(
        "--plan",
        choices=sorted(PLAN_ALLOWANCE),
        default="max",
        help="Perplexity plan whose monthly allowance you are spending (default: max)",
    )
    args = parser.parse_args(argv)
    rows = read_log(args.log)
    if not rows:
        print("empty log", file=sys.stderr)
        return 1
    print(render(report(rows, args.plan)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
