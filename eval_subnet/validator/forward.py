import hashlib
import math

import bittensor as bt
import numpy as np

from eval_subnet.protocol import (
    GeneratorSynapse,
    DiscriminatorSynapse,
    SolverSynapse,
)
from eval_subnet.validator.reward import (
    score_generator,
    score_discriminator,
    score_solver,
)
from eval_subnet.validator.routing import (
    discriminator_subset_for_epoch,
    solver_subset_for_problem,
)
from eval_subnet.oracles import lean, docker_grader, chutes, novelty
from eval_subnet.utils.uids import get_random_uids


async def forward(self):
    epoch = self.step
    cfg = self.config.neuron
    band_min = getattr(cfg, "difficulty_target_min", 0.75)
    band_max = getattr(cfg, "difficulty_target_max", 0.95)
    k_disc = getattr(cfg, "k_discriminators", 20)
    k_solv = getattr(cfg, "k_solvers", 3)
    corpus_index_path = getattr(cfg, "corpus_index_path", None)
    panel = _parse_panel(getattr(cfg, "frontier_panel", None))

    miner_uids = list(get_random_uids(self, k=cfg.sample_size))

    # Phase 1: collect generator submissions
    generator_responses = await self.dendrite(
        axons=[self.metagraph.axons[uid] for uid in miner_uids],
        synapse=GeneratorSynapse(domain="code_python"),
        deserialize=True,
    )
    bt.logging.info(f"epoch {epoch}: {len(generator_responses)} generator submissions")

    # Phase 2: validity gate. Drop submissions whose proof or grader doesn't pass.
    # Pin the panel snapshot at acceptance time so difficulty drift is observable.
    accepted = []
    for uid, resp in zip(miner_uids, generator_responses):
        if not _validity_gate(resp):
            continue
        panel_result = await chutes.panel_inference(resp.statement_formal, panel=panel, epoch=epoch)
        failrate = chutes.frontier_failrate(panel_result)
        if not (band_min <= failrate <= band_max):
            continue
        accepted.append({
            "gen_uid": uid,
            "resp": resp,
            "problem_hash": _hash_problem(resp),
            "panel_result": panel_result,
            "panel_failrate": failrate,
        })
    bt.logging.info(f"epoch {epoch}: {len(accepted)} passed validity + difficulty gates")

    # Phase 3: route to discriminator subset (hash-stable, commit-reveal salt is per-epoch)
    salt = self._epoch_salt(epoch) if hasattr(self, "_epoch_salt") else b""
    discriminator_uids = discriminator_subset_for_epoch(epoch, miner_uids, k_disc, salt)
    discriminator_results = {}
    for problem in accepted:
        responses = await self.dendrite(
            axons=[self.metagraph.axons[uid] for uid in discriminator_uids],
            synapse=DiscriminatorSynapse(
                domain=problem["resp"].domain,
                target_problem_hash=problem["problem_hash"],
            ),
            deserialize=True,
        )
        discriminator_results[problem["problem_hash"]] = [
            (uid, r.contamination_confidence) for uid, r in zip(discriminator_uids, responses)
        ]

    # Phase 4: route to solver subset (validator-assigned, k>=3, hash-stable per problem)
    solver_results = {}
    for problem in accepted:
        solver_uids = solver_subset_for_problem(
            epoch, problem["problem_hash"], miner_uids, k_solv, salt
        )
        responses = await self.dendrite(
            axons=[self.metagraph.axons[uid] for uid in solver_uids],
            synapse=SolverSynapse(
                domain=problem["resp"].domain,
                target_problem_hash=problem["problem_hash"],
            ),
            deserialize=True,
        )
        # Validator independently runs the grader. Solver's claim is not trusted.
        graded = [
            (uid, _grade_solution(problem["resp"], r)) for uid, r in zip(solver_uids, responses)
        ]
        solver_results[problem["problem_hash"]] = graded

    # Phase 5: score per role
    scores = np.zeros(len(self.metagraph.uids), dtype=np.float64)

    for problem in accepted:
        ph = problem["problem_hash"]
        novelty_val = novelty.novelty_score(
            statement_formal=problem["resp"].statement_formal,
            statement_natural=problem["resp"].statement_natural,
            domain=problem["resp"].domain,
            corpus_index_path=corpus_index_path,
            panel_result=problem["panel_result"],
        )
        disc_calls = discriminator_results.get(ph, [])
        disc_consensus_novel = (
            1.0 - (sum(c for _, c in disc_calls) / len(disc_calls)) if disc_calls else 0.5
        )
        solver_calls = solver_results.get(ph, [])
        solver_failrate = (
            1.0 - (sum(int(g) for _, g in solver_calls) / len(solver_calls))
            if solver_calls else 0.0
        )
        scores[problem["gen_uid"]] += score_generator(
            valid=True,
            novelty=novelty_val,
            discriminator_consensus=disc_consensus_novel,
            solver_failrate=solver_failrate,
            proof_complexity=_proof_complexity(problem["resp"]),
        )

    for ph, calls in discriminator_results.items():
        peer_consensus = (sum(c for _, c in calls) / len(calls)) if calls else 0.5
        for disc_uid, conf in calls:
            # TODO wire calibration set; ground_truth comes from novelty.calibration submodule
            scores[disc_uid] += score_discriminator(
                contamination_confidence=conf,
                ground_truth=None,
                peer_consensus=peer_consensus,
                is_calibration_problem=False,
                caught_calibration=False,
            )

    for ph, calls in solver_results.items():
        for solver_uid, passed in calls:
            scores[solver_uid] += score_solver(grader_passed=passed)

    # Phase 6: write scores. Multi-mech weight split is configured at the chain level
    # via sudo_set_mechanism_emission_split; the validator just reports per-UID scores.
    self.update_scores(scores, list(self.metagraph.uids))


def _validity_gate(resp: GeneratorSynapse) -> bool:
    if resp.domain == "math_lean4":
        return lean.typecheck(resp.statement_formal, resp.formal_solution)
    if resp.domain in ("code_python", "code_rust"):
        return docker_grader.run_grader(resp.grader_artifact_hash, resp.formal_solution)
    return False


def _grade_solution(generator_resp: GeneratorSynapse, solver_resp: SolverSynapse) -> bool:
    if generator_resp.domain == "math_lean4":
        return lean.typecheck(generator_resp.statement_formal, solver_resp.proposed_solution)
    if generator_resp.domain in ("code_python", "code_rust"):
        return docker_grader.run_grader(generator_resp.grader_artifact_hash, solver_resp.proposed_solution)
    return False


def _hash_problem(resp: GeneratorSynapse) -> str:
    h = hashlib.sha256()
    h.update(resp.statement_formal.encode())
    h.update(resp.grader_artifact_hash.encode())
    return h.hexdigest()


def _proof_complexity(resp: GeneratorSynapse) -> float:
    return min(1.0, math.log(max(1, len(resp.formal_solution))) / math.log(10000))


def _parse_panel(value):
    if value is None or value == "":
        return None
    if isinstance(value, list):
        return value
    return [s.strip() for s in str(value).split(",") if s.strip()]
