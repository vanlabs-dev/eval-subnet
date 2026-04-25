from typing import Optional
import bittensor as bt

from . import ngram, lsh, ast_fingerprint, frontier_confidence, embedding, calibration


LAYER_WEIGHTS = {
    "ngram": 0.25,
    "lsh": 0.20,
    "ast_fingerprint": 0.20,
    "frontier_confidence": 0.20,
    "embedding": 0.15,
}


def novelty_score(
    statement_formal: str,
    statement_natural: str = "",
    domain: str = "code_python",
    corpus_index_path: Optional[str] = None,
    panel_result: Optional[dict] = None,
) -> float:
    """Layered contamination detection. Returns novelty in [0, 1]; higher is more novel.

    Each submodule returns a contamination signal in [0, 1]; higher means more contaminated.
    Final novelty = 1 - weighted_sum(layer_signals).
    """
    if corpus_index_path is None:
        bt.logging.warning("novelty_score: no corpus index configured; returning 1.0")
        return 1.0

    signals = {
        "ngram": ngram.longest_match_score(statement_natural or statement_formal, corpus_index_path),
        "lsh": lsh.minhash_lsh_score(statement_natural or statement_formal, corpus_index_path),
        "ast_fingerprint": ast_fingerprint.fingerprint_match_score(statement_formal, domain, corpus_index_path),
        "frontier_confidence": frontier_confidence.memorization_signal(panel_result),
        "embedding": embedding.cosine_similarity_score(statement_natural or statement_formal, corpus_index_path),
    }

    contamination = sum(LAYER_WEIGHTS[k] * v for k, v in signals.items())
    return max(0.0, 1.0 - contamination)
