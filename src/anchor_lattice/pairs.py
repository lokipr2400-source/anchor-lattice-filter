"""Preference-pair scoring. Raw {chosen, rejected} in -> scored pair out."""

from __future__ import annotations

from typing import Any, Sequence

from .filter import filter_batch
from .spec import SPEC_VERSION


def score_pairs(
    pairs: Sequence[dict[str, Any]],
    backend: str = "hash",
    keep_rule: str = "both",
) -> dict[str, Any]:
    if keep_rule not in {"both", "any"}:
        raise ValueError("keep_rule must be 'both' or 'any'")

    texts: list[str] = []
    for i, pair in enumerate(pairs):
        if "chosen" not in pair or "rejected" not in pair:
            raise ValueError(f"pair {i} needs chosen and rejected")
        texts.append(str(pair["chosen"]))
        texts.append(str(pair["rejected"]))

    scored = filter_batch(texts, backend=backend)
    items = scored["items"]
    out_pairs = []
    n_keep = 0
    for i, pair in enumerate(pairs):
        ch, rj = items[2 * i], items[2 * i + 1]
        if keep_rule == "both":
            keep = bool(ch["keep"] and rj["keep"])
            reason = "keep" if keep else "side_dropped"
        else:
            keep = bool(ch["keep"] or rj["keep"])
            reason = "keep" if keep else "both_dropped"
        if keep:
            n_keep += 1
        out_pairs.append(
            {
                "id": pair.get("id", i),
                "keep": keep,
                "reason": reason,
                "keep_rule": keep_rule,
                "chosen": {
                    "text": ch["text"],
                    "keep": ch["keep"],
                    "reason": ch["reason"],
                    "H_hat": ch["H_hat"],
                    "B": ch["B"],
                    "U": ch["U"],
                    "W": ch["W"],
                },
                "rejected": {
                    "text": rj["text"],
                    "keep": rj["keep"],
                    "reason": rj["reason"],
                    "H_hat": rj["H_hat"],
                    "B": rj["B"],
                    "U": rj["U"],
                    "W": rj["W"],
                },
            }
        )
    return {
        "spec_version": SPEC_VERSION,
        "backend": scored["backend"],
        "keep_rule": keep_rule,
        "N_in": len(pairs),
        "N_kept": n_keep,
        "N_dropped": len(pairs) - n_keep,
        "pairs": out_pairs,
    }
