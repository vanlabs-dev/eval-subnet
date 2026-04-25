# Eval Subnet

Bittensor subnet that produces uncontaminated evaluation problems for frontier labs and AI Safety Institutes.

Beachhead: code (SWE-bench-Pro-style sandboxed Docker graders). Math (Lean 4 + mathlib4) added later.

Mechanism: three-role GAN-style (generator + discriminator + solver miners), inspired by Macrocosmos' [Apex 3.0](https://macrocosmosai.substack.com/p/apex-30-game-theoretic-ai-on-bittensor) and [GAN-style cross-miner oversight](https://macrocosmosai.substack.com/p/sn1-apex-introducing-gan-style-activity). Cross-subnet judgement oracle layered on top.

## Relationship to Apex

We borrow the adversarial-game pattern from Apex 3.0 (SN1). The product, scoring, and ground truth differ:

| | Apex (SN1) | Eval Subnet |
|---|---|---|
| Roles | 2 (generator + discriminator) | 3 (+ solver) |
| Who creates problems | Validator | Generator-miners |
| Ground truth | Validator's reference, string + semantic similarity | Mechanical: Lean kernel typecheck or sandboxed test suite |
| Domain | General conversation | Math + competitive programming |
| Buyer | API consumers, app builders | Frontier labs and AI Safety Institutes |
| Anti-contamination layer | n/a | Embargo, canary strings, rolling release, calibration injection |

Pattern attribution: the GAN-style cross-miner oversight design is Macrocosmos' contribution. This subnet extends it.

## Status

Skeleton. Synapses defined. Validator forward, reward functions, and oracle interfaces stubbed. Real Lean kernel wrapper works if `lean` is on PATH; Docker grader, Chutes inference, novelty embedding are next.

## Layout

```
eval_subnet/
  protocol.py              GeneratorSynapse, DiscriminatorSynapse, SolverSynapse
  validator/
    forward.py             per-tempo orchestration
    reward.py              three role-specific scoring functions
  oracles/
    lean.py                Lean 4 kernel typecheck wrapper
    docker_grader.py       SWE-bench-Pro-style sandbox runner
    chutes.py              SN64 frontier-panel inference client
    novelty.py             embedding-based contamination detection
  base/, api/, utils/, mock/   from bittensor-subnet-template
neurons/
  miner.py                 role-aware miner
  validator.py             validator entry point
```

## Roles

| Role | Submits |
|---|---|
| Generator | `(statement, formal_solution, grader)` |
| Discriminator | confidence in [0, 1] + optional evidence URL |
| Solver | proposed solution + success bool |

## Validator forward (per tempo)

1. Solicit generator submissions
2. Validity-gate via Lean kernel / Docker grader
3. Route candidates to discriminator-miners (hash-stable random routing)
4. Route to a hash-stable subset of solver-miners (k>=3)
5. Score per role per `reward.py`
6. `update_scores` per mechanism

## Oracle stack

| Oracle | Source | Status |
|---|---|---|
| Lean 4 kernel | local toolchain (elan + lake) | works if `lean` on PATH |
| Docker grader | local Docker daemon | stub |
| Frontier panel | Chutes (SN64), Intel TDX TEE | stub |
| Novelty | embedding model + corpus index | stub |

## Multi-mechanism

Three mechanisms with `sudo_set_mechanism_emission_split([32767, 16384, 16384])` for [50%, 25%, 25%] (generator-heavy at launch).

## Local dev

```bash
pip install -e .
pytest tests/
```

## License

MIT.
