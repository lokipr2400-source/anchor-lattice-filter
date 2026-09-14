"""CLI: python -m anchor_lattice.cli examples/batch.json"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .filter import filter_batch
from .spec import SPEC_FROZEN_ON, SPEC_VERSION


def _load(path: Path) -> tuple[list[str], list[str] | None]:
    raw = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        data = json.loads(raw)
        if isinstance(data, list):
            if data and isinstance(data[0], dict):
                texts = [str(d["text"]) for d in data]
                poles = [str(d.get("pole", "none")) for d in data]
                return texts, poles
            return [str(x) for x in data], None
        raise SystemExit("JSON must be a list of strings or {text, pole} objects.")
    texts = [line.strip() for line in raw.splitlines() if line.strip()]
    return texts, None


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description=f"Anchor Lattice Filter spec {SPEC_VERSION} frozen {SPEC_FROZEN_ON}"
    )
    p.add_argument("input", help="JSON list or plaintext file, one statement per line")
    p.add_argument("--embed", default="hash", choices=["hash", "minilm"])
    p.add_argument("--pretty", action="store_true")
    args = p.parse_args(argv)

    path = Path(args.input)
    if not path.exists():
        print(f"file not found: {path}", file=sys.stderr)
        return 2
    texts, poles = _load(path)
    if not texts:
        print("empty input", file=sys.stderr)
        return 2
    out = filter_batch(texts, poles=poles, backend=args.embed)
    print(json.dumps(out, indent=2 if args.pretty else None, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
