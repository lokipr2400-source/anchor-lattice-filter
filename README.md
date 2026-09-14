# Anchor Lattice Filter

Frozen spec **v1.0.0** (2026-09-14) for the entropy-gated + opposition-balanced keep/drop rule.

This repository is the public, runnable core of **Module A** of the Anchor Lattice Framework. It is not the LESFC cryptographic membrane and not the holographic hardware claims.

A stranger should be able to clone and run it with Python 3.10+ and `numpy`.

## Clone and run

```bash
git clone https://github.com/lokipr2400-source/anchor-lattice-filter.git
cd anchor-lattice-filter
python -m pip install -e .
python -m anchor_lattice.cli examples/batch.json --pretty
python tests/test_filter.py
```

Optional MiniLM embeddings (downloads the model on first use):

```bash
python -m pip install sentence-transformers
python -m anchor_lattice.cli examples/batch.json --embed minilm --pretty
```

## What it does

Each statement in a batch is embedded, scored, and marked KEEP or DROP:

- local semantic entropy too low = collapse, too high = noise
- opposition balance B used in the score; pathological collapse is a hard drop only when poles are unlabeled
- near-duplicate of an already-kept item
- combined score W = 0.35(1-H)+0.40 B+0.25 U

Exact formulas and frozen constants: [SPEC.md](SPEC.md).

## Python API

```python
from anchor_lattice import filter_batch

out = filter_batch(
    ["Keep updates small during scale jumps.", "asdf noise token salad 1234"],
    backend="hash",
)
print(out["kept"], out["items"][0]["reason"])
```

## License

MIT for this public filter implementation only.
