"""Functional demo: raw preference JSONL in, scored pairs out."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .pairs import score_pairs
from .spec import SPEC_FROZEN_ON, SPEC_VERSION


def _load_pairs(path: Path) -> list[dict]:
    raw = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".jsonl":
        pairs = []
        for line in raw.splitlines():
            line = line.strip()
            if line:
                pairs.append(json.loads(line))
        return pairs
    data = json.loads(raw)
    if not isinstance(data, list):
        raise SystemExit("JSON must be a list of {chosen, rejected} objects")
    return data


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description=(
            f"Raw preference pairs in -> scored/filtered pairs out. "
            f"spec {SPEC_VERSION} frozen {SPEC_FROZEN_ON}"
        )
    )
    p.add_argument("input", help="JSONL or JSON list of {chosen, rejected}")
    p.add_argument("--embed", default="hash", choices=["hash", "minilm"])
    p.add_argument("--keep-rule", default="both", choices=["both", "any"])
    p.add_argument("--pretty", action="store_true")
    args = p.parse_args(argv)
    path = Path(args.input)
    if not path.exists():
        print(f"file not found: {path}", file=sys.stderr)
        return 2
    pairs = _load_pairs(path)
    if not pairs:
        print("empty input", file=sys.stderr)
        return 2
    out = score_pairs(pairs, backend=args.embed, keep_rule=args.keep_rule)
    print(json.dumps(out, indent=2 if args.pretty else None, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
