from typing import Optional
import bittensor as bt


DEFAULT_INJECTION_RATE = 1 / 25
DEFAULT_REFRESH_DAYS = 30


def sample_ground_truth_check(problem_hash: str, sampled_corpus_path: str) -> Optional[float]:
    """Periodic expensive corpus crawl on a sample of accepted problems.

    Anchors the discriminator-miner pool's calibration. Run on a fraction of accepted
    problems per epoch (default 1 in 25). The held-out corpus is refreshed every
    `calibration_corpus_refresh_days` days (default 30, aligned with LiveBench /
    LiveCodeBench monthly cadence).

    Faster refresh narrows the window in which the held-out corpus itself can be
    contaminated by ongoing frontier-model training. Slower refresh saves operational
    cost. Quarterly is available as a budget-constrained option but is not the default.

    Returns ground-truth contamination score in [0, 1], or None if not sampled this epoch.
    """
    bt.logging.warning("calibration.sample_ground_truth_check stubbed")
    return None


def is_calibration_problem(problem_hash: str, calibration_set: set) -> bool:
    """Check if a problem hash matches a validator-injected synthetic-contaminated problem.

    Discriminators that fail to flag injected problems as contaminated get slashed.
    """
    return problem_hash in calibration_set
