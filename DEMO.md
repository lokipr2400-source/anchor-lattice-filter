# Functional demo

Raw preference text in. Scored / filtered pairs out. No hardcoded metric slogans.

```bash
python -m anchor_lattice.demo examples/raw_pairs.jsonl --pretty
```

Each output pair has `keep`, per-side `H_hat`, `B`, `U`, `W`, and a reason.
Default `keep_rule=both`: the pair is kept only if **both** sides KEEP. That rule does not look at which side is labeled chosen.

This demo is the filter. It is not a novel, not JAR Theory, and not an 8B to 70B run.

JAR Theory of Progressive Evolution is personal philosophy. It is not a variable in the filter and has no test in this repository.
Distributed Childhood and related stories are fiction. They are not evidence that the filter works.
