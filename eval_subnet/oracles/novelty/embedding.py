import bittensor as bt


DEFAULT_THRESHOLD = 0.85


def cosine_similarity_score(statement: str, corpus_index_path: str) -> float:
    """Dense-embedding cosine-similarity signal. Returns [0, 1]; higher = closer in embedding space.

    Cheap fallback. Catches semantic paraphrases that defeat n-gram and LSH but isn't
    reliable on its own (high false-positive rate per ACL 2025 survey). Used as a soft
    weight in the layered orchestrator, not a sole gate.
    """
    bt.logging.warning("embedding.cosine_similarity_score stubbed")
    return 0.0
