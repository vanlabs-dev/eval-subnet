from typing import Optional
import bittensor as bt


LOW_TEMP_THRESHOLD = 0.1
DEFAULT_QUORUM = 0.75


def memorization_signal(
    panel_result: Optional[dict],
    quorum_threshold: float = DEFAULT_QUORUM,
) -> float:
    """Inverse-MIA contamination signal. Returns [0, 1]; higher = likely memorized.

    Two patterns trigger:

    1. Quorum solve at low temperature: at least `quorum_threshold` of the panel solves
       the candidate at low temp. Single-model solve does not trigger; this prevents
       one strong model with a wide training set from driving false positives.

    2. Elder-only solve: elder-tier models solve while flagship-tier models do not.
       Strongest contamination signal, since it points to memorization in an older
       training corpus that newer models trained around or unlearned. The panel
       result includes per-model cutoff metadata for this comparison.

    Expects the pinned panel snapshot dict from `oracles.chutes.panel_inference`.
    """
    if panel_result is None:
        return 0.0

    results = panel_result.get("results", [])
    if not results:
        return 0.0

    solve_rate = sum(1 for r in results if r) / len(results)
    if solve_rate < quorum_threshold:
        # TODO check elder-only solve pattern via cutoffs metadata
        return 0.0

    bt.logging.warning("frontier_confidence.memorization_signal stubbed")
    return 0.0
