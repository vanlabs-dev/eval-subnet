from typing import Literal
import bittensor as bt
from pydantic import Field


Domain = Literal["math_lean4", "code_python", "code_rust"]


class _BaseEvalSynapse(bt.Synapse):
    domain: Domain
    collateral_bond_tx: str = ""
    response_score: float = 0.0


class GeneratorSynapse(_BaseEvalSynapse):
    statement_natural: str = ""
    statement_formal: str = ""
    formal_solution: str = ""
    grader_artifact_hash: str = ""
    novelty_attestation: dict = Field(default_factory=dict)

    def deserialize(self) -> "GeneratorSynapse":
        return self


class DiscriminatorSynapse(_BaseEvalSynapse):
    target_problem_hash: str = ""
    contamination_confidence: float = 0.0
    evidence_url: str = ""

    def deserialize(self) -> "DiscriminatorSynapse":
        return self


class SolverSynapse(_BaseEvalSynapse):
    target_problem_hash: str = ""
    proposed_solution: str = ""
    solve_success: bool = False

    def deserialize(self) -> "SolverSynapse":
        return self
