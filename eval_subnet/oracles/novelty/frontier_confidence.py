from typing import Optional
import bittensor as bt


LOW_TEMP_THRESHOLD = 0.1
DEFAULT_QUORUM = 0.75


def memorization_signal(
    panel_result: Optional[dict],
    quorum_threshold: float = DEFAULT_QUORUM,
) -> float:
    """Inverse-MIA contamination signal. Returns [0, 1]; higher = likely memorized.

    A problem is flagged as likely-memorized only when the fraction of panel models that
    solve it at low temperature meets or exceeds `quorum_threshold`. Single-model solve
    does not trigger; this prevents one strong model with a wide training set from
    driving false positives.

    Expects the pinned panel snapshot dict from `oracles.chutes.panel_inference`.
    """
    if panel_result is None:
        return 0.0

    results = panel_result.get("results", [])
    if not results:
        return 0.0

    solve_rate = sum(1 for r in results if r) / len(results)
    if solve_rate < quorum_threshold:
        return 0.0

    bt.logging.warning("frontier_confidence.memorization_signal stubbed")
    return 0.0
