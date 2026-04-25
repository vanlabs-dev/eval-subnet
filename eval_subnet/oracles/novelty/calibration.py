from typing import Optional
import bittensor as bt


DEFAULT_INJECTION_RATE = 1 / 25


def sample_ground_truth_check(problem_hash: str, sampled_corpus_path: str) -> Optional[float]:
    """Periodic expensive corpus crawl on a sample of accepted problems.

    Anchors the discriminator-miner pool's calibration. Run on a fraction of accepted
    problems per epoch (default 1 in 25). Held-out corpus is refreshed quarterly to
    prevent discriminators from learning the calibration distribution.

    Returns ground-truth contamination score in [0, 1], or None if not sampled this epoch.
    """
    bt.logging.warning("calibration.sample_ground_truth_check stubbed")
    return None


def is_calibration_problem(problem_hash: str, calibration_set: set) -> bool:
    """Check if a problem hash matches a validator-injected synthetic-contaminated problem.

    Discriminators that fail to flag injected problems as contaminated get slashed.
    """
    return problem_hash in calibration_set
