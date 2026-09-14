# Measured comparison — spec v1.0.0

**Run date:** 2026-09-14  
**Embedding backend actually used:** `hash-3gram-384-seed-20260914` (not MiniLM)  
**No prior marketing numbers are restated here.** Keep/drop rates below are counts from this run only.

## Named dataset and split

| Field | Value |
|---|---|
| Dataset | Anthropic HH-RLHF, config `helpful-base` |
| Source | https://huggingface.co/datasets/Anthropic/hh-rlhf |
| Paper | Bai et al., 2022, arXiv:2204.05862 |
| License | MIT |
| Official train | 43,835 preference pairs |
| Official test | 2,354 preference pairs |
| Eval split | **official test only** (not shuffled off train) |
| Eval unit | last Assistant utterance from chosen and from rejected |
| N pairs eval | 2,354 |
| N statements eval | 4,708 (= 2 × 2,354) |
| Empty last-turn rejected | 4 |
| Empty last-turn chosen | 0 |

Train was counted, not filtered. All method comparisons use the same 4,708 test statements.

## Methods

1. **no_filter** — keep every statement.
2. **entropy_only** — drop short (len < 12), low_entropy (H < 0.15), high_entropy (H > 0.985). No score gate, no duplicate gate, no B gate.
3. **anchor_filter_v1.0.0** — frozen spec (entropy + opposition score + duplicate + W).

## Table 1 — statement keep / drop

Wilson 95% interval on keep rate. Denominator is always N_in = 4708.

| Method | N_in | N_kept | N_dropped | Keep rate | Wilson 95% CI |
|---|---:|---:|---:|---:|---|
| no_filter | 4708 | 4708 | 0 | 1.000 | [0.999, 1.000] |
| entropy_only | 4708 | 4241 | 467 | 0.901 | [0.892, 0.909] |
| anchor_filter_v1.0.0 | 4708 | 3380 | 1328 | 0.718 | [0.705, 0.731] |

Drop share vs no_filter: entropy_only 467/4708 = 9.92%; full filter 1328/4708 = 28.21%.

## Table 2 — drop reasons (counts)

| Reason | no_filter | entropy_only | anchor_filter_v1.0.0 |
|---|---:|---:|---:|
| keep | 4708 | 4241 | 3380 |
| short | 0 | 69 | 69 |
| high_entropy | 0 | 398 | 398 |
| low_entropy | 0 | 0 | 0 |
| low_score | 0 | — | 855 |
| duplicate | 0 | — | 5 |
| unbalanced | 0 | — | 1 |

## Table 3 — chosen vs rejected

Each side has denominator N = 2354. Delta = P(keep|chosen) − P(keep|rejected), bootstrap 2000 pair resamples, seed 20260914.

| Method | Kept chosen | P(keep|chosen) [CI] | Kept rejected | P(keep|rejected) [CI] | Δ pp [boot 95% CI] |
|---|---:|---|---:|---|---|
| no_filter | 2354 | 1.000 [0.998, 1.000] | 2354 | 1.000 [0.998, 1.000] | 0.00 [0.00, 0.00] |
| entropy_only | 2155 | 0.915 [0.904, 0.926] | 2086 | 0.886 [0.873, 0.898] | +2.93 [+1.36, +4.59] |
| anchor_filter_v1.0.0 | 1718 | 0.730 [0.712, 0.747] | 1662 | 0.706 [0.687, 0.724] | +2.38 [+0.13, +4.76] |

The chosen/rejected keep gap is small. The full-filter bootstrap interval excludes 0 but the effect is about two to three percentage points.

## Table 4 — pair outcomes (N_pairs = 2354)

| Outcome | no_filter | entropy_only | anchor_filter_v1.0.0 |
|---|---:|---:|---:|
| both kept | 2354 | 1928 | 1280 |
| chosen only | 0 | 227 | 438 |
| rejected only | 0 | 158 | 382 |
| neither | 0 | 41 | 254 |

## Table 5 — hash-space geometry

| Method | mean pairwise cos (kept) | mean H kept | mean H dropped |
|---|---:|---:|---:|
| no_filter | 0.218 | 0.970 | — |
| entropy_only | 0.246 | 0.969 | 0.986 |
| anchor_filter_v1.0.0 | 0.263 | 0.973 | 0.963 |

On this backend the kept set is slightly more clustered than the raw set.

## What this run does not show

- No hallucination rate was measured.
- No training-token or preference-data multiplier.
- No scale-jump continuity number.
- MiniLM was not used.
- Train was not filtered.

Machine-readable copy: results.json.
