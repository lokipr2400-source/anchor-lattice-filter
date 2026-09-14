# Anchor Lattice Filter

Frozen spec **v1.0.0** (2026-09-14) for the entropy-gated + opposition-balanced keep/drop rule.

This repository is the public, runnable core of Module A of the Anchor Lattice Framework. It is not the LESFC cryptographic membrane and not the holographic hardware claims.

A stranger should be able to clone and run it with Python 3.10+ and numpy.

## Clone and run

```bash
git clone https://github.com/lokipr2400-source/anchor-lattice-filter.git
cd anchor-lattice-filter
python -m pip install -e .
python -m anchor_lattice.cli examples/batch.json --pretty
python -m anchor_lattice.demo examples/raw_pairs.jsonl --pretty
python tests/test_filter.py
```

Pair demo: [DEMO.md](DEMO.md).
Held-out counts: [RESULTS.md](RESULTS.md).
Small linear probe (not an 8B/70B train): [probe.json](probe.json).

## License

MIT for this public filter implementation only.
