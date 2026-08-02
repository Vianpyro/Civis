"""CLI: python -m pipeline.run --election fr-2027 [--step fetch|extract|generate|impacts|all]

`--limit` and `--force` belong to the impacts step alone (DT-24): what they cap
and what they redo is a model call, and no other step makes one on a per-point
basis.
"""

from __future__ import annotations

import argparse
import sys

from . import extract, fetch, generate, impacts

STEPS = {
    "fetch": fetch.main,
    "extract": extract.main,
    "generate": generate.main,
    "impacts": impacts.main,
}

# `all` stops before the two drafting steps: a model call costs money and needs a
# human reviewer, so it is always an explicit choice (DT-28).
ALL = ["fetch", "extract"]


def main() -> int:
    parser = argparse.ArgumentParser(prog="pipeline.run")
    parser.add_argument("--election", default="fr-2027")
    parser.add_argument("--step", choices=[*STEPS, "all"], default="all")
    parser.add_argument("--limit", type=int, help="impacts: at most N points in this run")
    parser.add_argument("--force", action="store_true", help="impacts: redraft even if `of` still matches")
    args = parser.parse_args()

    steps = ALL if args.step == "all" else [args.step]
    for name in steps:
        print(f"== {name} ==")
        flags = {"limit": args.limit, "force": args.force} if name == "impacts" else {}
        code = STEPS[name](args.election, **flags)
        if code != 0:
            return code
    return 0


if __name__ == "__main__":
    sys.exit(main())
