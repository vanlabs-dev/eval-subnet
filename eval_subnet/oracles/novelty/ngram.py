import bittensor as bt


DEFAULT_N = 7


def longest_match_score(statement: str, corpus_index_path: str) -> float:
    """LONGEST-MATCH n-gram contamination signal. Returns [0, 1]; higher = more contaminated.

    Per Ishikawa 2025 / ACL 2025 contamination survey, LONGEST-MATCH with n < 8 is the most
    effective n-gram metric for benchmark contamination detection.
    """
    bt.logging.warning("ngram.longest_match_score stubbed")
    return 0.0
