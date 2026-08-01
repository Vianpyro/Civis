"""CLI: python -m pipeline.run --election fr-2027 [--step fetch|extract|generate|all]"""

from __future__ import annotations

import argparse
import sys

from . import extract, fetch, generate

STEPS = {"fetch": fetch.main, "extract": extract.main, "generate": generate.main}


def main() -> int:
    parser = argparse.ArgumentParser(prog="pipeline.run")
    parser.add_argument("--election", default="fr-2027")
    parser.add_argument("--step", choices=[*STEPS, "all"], default="all")
    # `all` stops before generate: drafting questions costs money and needs a
    # human reviewer, so it is always an explicit choice.
    args = parser.parse_args()

    steps = ["fetch", "extract"] if args.step == "all" else [args.step]
    for name in steps:
        print(f"== {name} ==")
        code = STEPS[name](args.election)
        if code != 0:
            return code
    return 0


if __name__ == "__main__":
    sys.exit(main())
