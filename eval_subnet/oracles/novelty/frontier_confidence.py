from typing import Optional
import bittensor as bt


LOW_TEMP_THRESHOLD = 0.1


def memorization_signal(panel_result: Optional[dict]) -> float:
    """Inverse-MIA contamination signal. Returns [0, 1]; higher = likely memorized.

    If a panel of frontier models all solve the candidate problem at low temperature with
    high confidence, the problem was very likely in their training data. This is the only
    layer that detects deep semantic-equivalence contamination (where the surface form is
    novel but the underlying solution is memorized).

    Expects the pinned panel snapshot dict from `oracles.chutes.panel_inference`.
    """
    if panel_result is None:
        return 0.0

    bt.logging.warning("frontier_confidence.memorization_signal stubbed")
    return 0.0
