"""Embeddings: MiniLM opt-in, deterministic hashed 3-gram fallback."""

from __future__ import annotations

import hashlib
from typing import Iterable, List

import numpy as np

from .spec import BACKEND_FALLBACK, BACKEND_MINILM, EMBED_DIM, FALLBACK_HASH_SEED


def _l2_normalize(mat: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(mat, axis=1, keepdims=True)
    norms = np.maximum(norms, 1e-12)
    return mat / norms


def _trigrams(text: str) -> List[str]:
    padded = f"  {text.lower()}  "
    return [padded[i : i + 3] for i in range(len(padded) - 2)]


def hash_embed(texts: Iterable[str]) -> np.ndarray:
    """Signed 3-gram hash to 384-d. Deterministic. No network."""
    rows = []
    prefix = str(FALLBACK_HASH_SEED).encode("utf-8")
    for text in texts:
        vec = np.zeros(EMBED_DIM, dtype=np.float64)
        for gram in _trigrams(text):
            digest = hashlib.sha256(prefix + gram.encode("utf-8")).digest()
            idx = int.from_bytes(digest[:4], "little") % EMBED_DIM
            sign = 1.0 if digest[4] & 1 else -1.0
            vec[idx] += sign
        rows.append(vec)
    return _l2_normalize(np.vstack(rows) if rows else np.zeros((0, EMBED_DIM)))


def minilm_embed(texts: Iterable[str]) -> np.ndarray:
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise RuntimeError(
            "sentence-transformers is not installed. "
            "pip install sentence-transformers  OR  use --embed hash"
        ) from exc
    model = SentenceTransformer(BACKEND_MINILM)
    vecs = model.encode(list(texts), normalize_embeddings=True, convert_to_numpy=True)
    return np.asarray(vecs, dtype=np.float64)


def embed(texts: Iterable[str], backend: str = "hash") -> tuple[np.ndarray, str]:
    backend = backend.lower().strip()
    if backend in {"hash", "fallback", BACKEND_FALLBACK}:
        return hash_embed(texts), BACKEND_FALLBACK
    if backend in {"minilm", "primary", BACKEND_MINILM}:
        return minilm_embed(texts), BACKEND_MINILM
    raise ValueError(f"Unknown embed backend: {backend}")
