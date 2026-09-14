"""Entropy-gated + opposition-balanced keep/drop. Spec v1.0.0."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable, List, Optional, Sequence

import numpy as np

from .embed import embed
from .spec import (
    ALPHA,
    B_MIN,
    BETA,
    DUP_COS,
    EPS,
    GAMMA,
    H_MAX,
    H_MIN,
    MIN_CHARS,
    SPEC_VERSION,
    TAU,
    W_MIN,
)


@dataclass
class ItemResult:
    index: int
    text: str
    keep: bool
    reason: str
    H_hat: float
    B: float
    U: float
    W: float


def _softmax_entropy(cos_row: np.ndarray, tau: float) -> float:
    """Shannon entropy of temperature-softmax over other items. Natural log."""
    if cos_row.size <= 1:
        return 0.5
    logits = cos_row / tau
    logits = logits - logits.max()
    exps = np.exp(logits)
    probs = exps / (exps.sum() + EPS)
    H = float(-(probs * np.log(probs + EPS)).sum())
    return H / float(np.log(cos_row.size))


def local_entropy(E: np.ndarray) -> np.ndarray:
    n = E.shape[0]
    if n < 3:
        return np.full(n, 0.5, dtype=np.float64)
    sims = E @ E.T
    out = np.zeros(n, dtype=np.float64)
    for i in range(n):
        mask = np.ones(n, dtype=bool)
        mask[i] = False
        mask &= sims[i] < DUP_COS
        if mask.sum() < 2:
            out[i] = 0.5
        else:
            out[i] = _softmax_entropy(sims[i, mask], TAU)
    return out


def opposition_balance(E: np.ndarray, poles: Optional[Sequence[str]] = None) -> np.ndarray:
    n = E.shape[0]
    B = np.ones(n, dtype=np.float64)
    if n < 4:
        return B

    if poles is not None:
        labels = [p.lower().strip() if p else "none" for p in poles]
        if any(p in {"pro", "con"} for p in labels):
            pro_idx = [i for i, p in enumerate(labels) if p == "pro"]
            con_idx = [i for i, p in enumerate(labels) if p == "con"]
            if len(pro_idx) >= 2 and len(con_idx) >= 2:
                c_pos = E[pro_idx].mean(axis=0)
                c_neg = E[con_idx].mean(axis=0)
                return _balance_from_centroids(E, c_pos, c_neg)

    centered = E - E.mean(axis=0, keepdims=True)
    try:
        _, _, vt = np.linalg.svd(centered, full_matrices=False)
    except np.linalg.LinAlgError:
        return B
    axis = vt[0]
    proj = centered @ axis
    pro_idx = np.where(proj >= 0)[0]
    con_idx = np.where(proj < 0)[0]
    if len(pro_idx) < 2 or len(con_idx) < 2:
        return B
    c_pos = E[pro_idx].mean(axis=0)
    c_neg = E[con_idx].mean(axis=0)
    return _balance_from_centroids(E, c_pos, c_neg)


def _balance_from_centroids(E: np.ndarray, c_pos: np.ndarray, c_neg: np.ndarray) -> np.ndarray:
    c_pos = c_pos / max(np.linalg.norm(c_pos), EPS)
    c_neg = c_neg / max(np.linalg.norm(c_neg), EPS)
    m_pos = E @ c_pos
    m_neg = E @ c_neg
    return 1.0 - (np.abs(m_pos - m_neg) / (np.abs(m_pos) + np.abs(m_neg) + EPS))


def filter_batch(
    texts: Sequence[str],
    poles: Optional[Sequence[str]] = None,
    backend: str = "hash",
) -> dict:
    texts = list(texts)
    n = len(texts)
    E, backend_id = embed(texts, backend=backend)
    H = local_entropy(E)
    Bal = opposition_balance(E, poles=poles)
    sims = E @ E.T

    prelim = []
    for i, text in enumerate(texts):
        if len(text.strip()) < MIN_CHARS:
            prelim.append(("short", None))
            continue
        if H[i] < H_MIN:
            prelim.append(("low_entropy", None))
            continue
        if H[i] > H_MAX:
            prelim.append(("high_entropy", None))
            continue
        poles_used = poles is not None and any(
            (p or "").lower().strip() in {"pro", "con"} for p in poles
        )
        if (not poles_used) and Bal[i] < B_MIN:
            prelim.append(("unbalanced", None))
            continue
        W_raw = ALPHA * (1.0 - H[i]) + BETA * Bal[i] + GAMMA * 1.0
        prelim.append((None, W_raw))

    order = sorted(
        range(n),
        key=lambda i: prelim[i][1] if prelim[i][1] is not None else -1.0,
        reverse=True,
    )
    kept: List[int] = []
    reasons = ["pending"] * n
    U = np.ones(n, dtype=np.float64)
    W = np.zeros(n, dtype=np.float64)
    keep = [False] * n

    for i in order:
        hard, _ = prelim[i]
        if hard is not None:
            reasons[i] = hard
            U[i] = 1.0 if not kept else float(1.0 - max(float(sims[i, k]) for k in kept))
            W[i] = ALPHA * (1.0 - H[i]) + BETA * Bal[i] + GAMMA * U[i]
            continue
        if kept:
            max_cos = max(float(sims[i, k]) for k in kept)
            U[i] = 1.0 - max_cos
            if max_cos >= DUP_COS:
                reasons[i] = "duplicate"
                W[i] = ALPHA * (1.0 - H[i]) + BETA * Bal[i] + GAMMA * U[i]
                continue
        else:
            U[i] = 1.0
        W[i] = ALPHA * (1.0 - H[i]) + BETA * Bal[i] + GAMMA * U[i]
        if W[i] < W_MIN:
            reasons[i] = "low_score"
            continue
        keep[i] = True
        reasons[i] = "keep"
        kept.append(i)

    results = [
        ItemResult(
            index=i,
            text=texts[i],
            keep=keep[i],
            reason=reasons[i],
            H_hat=float(H[i]),
            B=float(Bal[i]),
            U=float(U[i]),
            W=float(W[i]),
        )
        for i in range(n)
    ]
    kept_poles = []
    if poles is not None:
        kept_poles = [
            (poles[i] or "none").lower().strip()
            for i in range(n)
            if keep[i] and (poles[i] or "none").lower().strip() in {"pro", "con"}
        ]
    n_pro = sum(p == "pro" for p in kept_poles)
    n_con = sum(p == "con" for p in kept_poles)
    batch_balance = (
        1.0 - abs(n_pro - n_con) / (n_pro + n_con + EPS) if kept_poles else None
    )
    return {
        "spec_version": SPEC_VERSION,
        "backend": backend_id,
        "kept": sum(keep),
        "dropped": n - sum(keep),
        "batch_balance": batch_balance,
        "items": [asdict(r) for r in results],
    }


def filter_texts(texts: Iterable[str], **kwargs) -> dict:
    return filter_batch(list(texts), **kwargs)
