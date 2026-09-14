# Anchor Lattice Filter — Frozen Spec v1.0.0

**Status:** FROZEN 2026-09-14. Changing any constant or formula is a new spec version.  
**Scope:** Module A only (entropy-gated + opposition-balanced keep/drop). Not LESFC. Not holographic hardware.

## Input

A batch of n UTF-8 texts. Optional pole in {pro, con, none}.

## Embedding (exact)

- Primary model: `sentence-transformers/all-MiniLM-L6-v2` (384-d, L2-normalized).
- Frozen fallback (always available): signed character 3-gram hashing into 384-d, seed `20260914`, then L2-normalize. Fallback is the default so a stranger can run with numpy only. Primary model is opt-in: `--embed minilm`.
- Cosine is the inner product of unit vectors.

## Local semantic entropy H-hat

Temperature tau = 0.15. Exclude self and near-duplicates (cos >= 0.92). If fewer than 2 remaining neighbors, H-hat := 0.5.

s_ij = exp(cos(e_i, e_j) / tau)
p_ij = s_ij / sum_k s_ik over neighbors N_i
H_i = -sum p_ij ln p_ij
H-hat_i = H_i / ln(|N_i|) in [0,1]
If n < 3 or |N_i| < 2 then H-hat := 0.5.

## Opposition balance B

If any item has pole set, centroids are means of those embeddings. Else split by sign of projection onto the first principal axis of centered E (SVD). If a pole has <2 items or n<4, B := 1.0.

m+_i = cos(e_i, c+)
m-_i = cos(e_i, c-)
B_i = 1 - |m+ - m-| / (|m+| + |m-| + 1e-12)

## Novelty and score

Process candidates in descending raw score. Novelty vs already-kept set K:

U_i = 1 - max_{k in K} cos(e_i, e_k)    (U_i = 1 if K empty)
W_i = 0.35 (1 - H-hat_i) + 0.40 B_i + 0.25 U_i

## Keep / drop (all thresholds frozen)

- len(text) < 12 → DROP short
- H-hat < 0.15 → DROP low_entropy
- H-hat > 0.985 → DROP high_entropy
- B < 0.05 and no pole labels on the batch → DROP unbalanced
- max cos to a kept item >= 0.92 → DROP duplicate
- W < 0.45 → DROP low_score
- else KEEP

B is primarily a scoring feature (weight 0.40). The hard B_min=0.05 gate only drops numerical collapse, not ordinary partisan statements. The kept-set pole ratio is reported as batch_balance.

Constants: tau=0.15, H_min=0.15, H_max=0.985, B_min=0.05, W_min=0.45, dup=0.92, alpha=0.35, beta=0.40, gamma=0.25, eps=1e-12, seed=20260914.

## Output

For each item: keep bool, reason, H-hat, B, U, W, embedding backend id.
