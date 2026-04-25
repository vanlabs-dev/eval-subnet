from typing import Optional


GENERATOR_ALPHA = 0.3
GENERATOR_BETA = 0.6
GENERATOR_GAMMA = 0.1


def score_generator(
    *,
    valid: bool,
    novelty: float,
    discriminator_consensus: float,
    solver_failrate: float,
    proof_complexity: float,
) -> float:
    if not valid:
        return 0.0
    if novelty < 0.7:
        return 0.0
    difficulty = discriminator_consensus * solver_failrate
    return (
        GENERATOR_ALPHA * novelty
        + GENERATOR_BETA * difficulty
        + GENERATOR_GAMMA * proof_complexity
    )


def score_discriminator(
    *,
    contamination_confidence: float,
    ground_truth: Optional[float],
    peer_consensus: float,
    is_calibration_problem: bool,
    caught_calibration: bool,
) -> float:
    if is_calibration_problem and not caught_calibration:
        return 0.0
    target = ground_truth if ground_truth is not None else peer_consensus
    return 1.0 - abs(contamination_confidence - target)


def score_solver(*, valid_solution: bool) -> float:
    return 1.0 if valid_solution else 0.0
