<div align="center">

# EVAL SUBNET

**Bonded, contamination-resistant evals for frontier AI on Bittensor**

*Three miner roles produce, vet, and stress-test fresh problems. Each ships with a stake-backed novelty attestation, anchored by layered contamination detection.*

![python](https://img.shields.io/badge/python-3.10%2B-3776AB) ![license](https://img.shields.io/badge/license-MIT-green) ![status](https://img.shields.io/badge/status-skeleton-orange)

</div>

---

Bittensor subnet building a permissionless contamination-detection R&D network. The product is the layered anti-contamination architecture: n-gram match, MinHash LSH, AST structural fingerprint, frontier-confidence inverse-MIA, and embedding similarity, anchored by periodic ground-truth corpus crawls. Buyers (frontier labs, AI Safety Institutes) get a stream of bonded, mechanically-verified, novelty-attested evaluation problems.

The three-role GAN mechanism (generator + discriminator + solver miners) is the incentive structure that pays contributors to keep the contamination layer evolving against frontier models. Inspired by Macrocosmos' [Apex 3.0](https://macrocosmosai.substack.com/p/apex-30-game-theoretic-ai-on-bittensor) and [GAN-style cross-miner oversight](https://macrocosmosai.substack.com/p/sn1-apex-introducing-gan-style-activity).

Beachhead: code-track in Python (SWE-bench-Pro-style sandboxed Docker graders). Code-track in Rust as a follow-up domain. Math-track (Lean 4 + mathlib4) added once the code track is stable. Cross-subnet judgement oracle layered on top.

Demand pull: OpenAI deprecated [SWE-bench Verified](https://www.swebench.com/) in favor of [SWE-bench Pro](https://labs.scale.com/leaderboard/swe_bench_pro_public) in early 2026 due to contamination concerns. Claude Opus 4.5 scored 80.9% on Verified vs 45.9% on Pro. Frontier labs are operationally paying the cost of contaminated benchmarks right now.

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

Skeleton. Synapses defined. Validator forward phases 1-6 wired against stubs. Reward functions, oracle public APIs, hash-stable routing with commit-reveal salt, validator-assigned solver subset, difficulty-band hyperparameter, pinned panel snapshot all in place.

Real implementation order:
1. **Docker grader** (Python first; the validity gate for the code-only beachhead)
2. **Chutes panel inference** (real API client; required for difficulty signal and frontier-confidence layer)
3. **Novelty layered modules** (n-gram and LSH first because cheapest; AST fingerprint Python-only at launch; embedding as soft fallback)
4. **Calibration injection wiring** in the discriminator scoring path
5. **Real Lean kernel** integration (math track; deferred until math track goes live)
6. **AST fingerprint** for Rust and Lean (deferred to their respective track go-lives)

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
    novelty/               layered contamination detection
      ngram.py               LONGEST-MATCH n-gram against corpus
      lsh.py                 MinHash LSH near-duplicate
      ast_fingerprint.py     Lean AST / tree-sitter structural hash
      frontier_confidence.py inverse-MIA panel-solve signal
      embedding.py           dense-embedding cosine similarity
      calibration.py         periodic ground-truth corpus crawl
  base/, api/, utils/, mock/   from bittensor-subnet-template
neurons/
  miner.py                 role-aware miner
  validator.py             validator entry point
```

## Roles

| Role | Submits | Scored on |
|---|---|---|
| Generator | `(statement, formal_solution, grader)` | validity (Lean kernel / Docker grader), novelty (layered), frontier-panel fail rate, solver fail rate |
| Discriminator | contamination confidence in [0, 1] + optional evidence URL | correlation with periodic ground-truth + peer consensus; calibration-injection misses are slashed |
| Solver | proposed solution | validator independently runs the grader on the submitted solution; the only signal is whether the grader passes |

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
| Novelty | layered: n-gram, MinHash LSH, AST fingerprint, frontier-confidence, embedding | stubs with public API |

## Multi-mechanism

Three mechanisms with `sudo_set_mechanism_emission_split([32767, 16384, 16384])` for [50%, 25%, 25%] (generator-heavy at launch).

**Graceful degradation when the discriminator pool is small.** The validator only computes a discriminator-consensus signal when at least `min_discriminators_per_problem` (default 3) responsive discriminators reply for a given problem. Below the floor, the generator is scored on novelty plus solver-failrate alone, so the mechanism stays functional through cold-start before a discriminator market forms.

## Lean toolchain pinning

Math-track validators MUST use the exact Lean version pinned in [`lean-toolchain`](lean-toolchain) at the repo root. Different versions produce different typecheck behavior and break ground-truth consistency across the validator set. The `oracles.lean.verify_toolchain()` helper checks the running `lean` against the pinned version and refuses to proceed on mismatch. Update the pinned version on a coordinated subnet rotation, not unilaterally.

## Calibration

Two distinct calibration layers, often conflated:

**Discriminator calibration.** Validators periodically inject synthetic-contaminated problems (lifted from a held-out corpus that's not in the public index). Discriminators that fail to flag them are slashed. Default injection rate: 1 in 25 problems. The held-out corpus is refreshed quarterly to prevent discriminators from learning the calibration distribution.

**Difficulty-curve calibration.** Generators are accepted only if frontier-panel fail rate falls in `[0.75, 0.95]` (the `difficulty_target_band` hyperparameter). Below 0.75 is too easy; above 0.95 is potentially nonsensical or unsolvable. Each accepted problem is timestamped with its acceptance epoch and the panel snapshot in use, so difficulty drift is observable as panel composition evolves.

## Limits of contamination detection

The contamination problem is genuinely unsolved at scale. Layered detection catches verbatim and near-verbatim lifts deterministically (n-gram + LSH + AST fingerprint, ~95% of librarian-style attacks). Deep semantic-equivalence contamination (the surface form is novel but the underlying solution is memorized) is detected probabilistically via frontier-confidence inversion and the discriminator-miner game; no current method is individually reliable for this.

The subnet's structural advantage is that the discriminator-miner pool is a market-driven contamination-detection R&D process, paid to invent novel detection methods. The validator's job is to provide periodic ground-truth grounding via expensive corpus crawl on a sample (the `calibration` submodule), not to solve detection alone.

### Scope of the AST fingerprint layer

Tree-sitter supports 141+ languages but each requires a custom canonicalization pass (rename locals, normalize literals, strip comments and whitespace). Launch coverage is intentionally narrow:

| Domain | Status at launch | Why |
|---|---|---|
| `code_python` | implemented at launch (real fingerprint module) | beachhead; aligned with SWE-bench Pro demand |
| `code_rust` | stub at launch; real implementation as a follow-up | second-priority code track |
| `math_lean4` | stub at launch; deferred until math track goes live | uses Lean kernel terms, not tree-sitter |

Until a domain's fingerprint is real, the layered orchestrator falls back to n-gram + LSH + embedding for that domain. AST fingerprint is one of five novelty layers; absence weakens but doesn't break the detection.

### Panel composition for inverse-MIA

A 1-of-N panel solve is a noisy signal. Defenses:

- **Quorum threshold** (`panel_quorum_threshold` hyperparameter, default 0.75): a problem is flagged as likely-memorized only when at least 75% of the panel solves it at low temperature. Single-model solve does not trigger.
- **Vendor diversity**: default panel spans 3 vendors (Anthropic, OpenAI, Google). Quarterly governance vote rotates panel composition; previous panel snapshot is pinned per accepted problem so historical scoring stays auditable.
- **Cutoff diversity at launch**: default panel pairs 3 flagship models with 3 elder models from the same vendors (Claude Opus 4.7 with Claude Sonnet 3.5, GPT-5.3 Codex with GPT-4o, Gemini 3.1 Pro with Gemini 1.5 Pro). Display names are used in config; the integration layer resolves them to actual Chutes endpoint IDs at call time. Per-model training cutoffs are recorded with each accepted problem in the panel snapshot. The strongest contamination signal is elder-solve-while-flagship-fails, which points to memorization in an older training corpus.

### Calibration corpus refresh interval

Quarterly is too slow given how fast frontier models consume new data. Default refresh cadence is **monthly** (`calibration_corpus_refresh_days` hyperparameter, default 30), aligned with [LiveCodeBench rolling release](https://livecodebench.github.io/) and [LiveBench monthly cadence](https://livebench.ai/livebench.pdf). Quarterly stays available as an option for budget-constrained operation but is not the default.

The held-out corpus stays disjoint from the public corpus index, so discriminators who overfit to "I have memorized the calibration set" still help with calibration-injection scoring while learning nothing useful for real contamination detection. The risk is that the held-out corpus itself becomes contaminated as frontier models scrape new data; faster refresh narrows this window.

## Local dev

```bash
pip install -e .
pytest tests/
```

## License

MIT.
