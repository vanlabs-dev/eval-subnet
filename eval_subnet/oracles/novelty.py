import bittensor as bt


def novelty_score(statement: str, corpus_index_path: str | None = None) -> float:
    if corpus_index_path is None:
        bt.logging.warning("novelty_score: no corpus index configured; returning 1.0")
        return 1.0

    bt.logging.warning("novelty_score stubbed")
    return 1.0
