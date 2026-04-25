import bittensor as bt


SUPPORTED_DOMAINS_AT_LAUNCH = {"code_python"}
PLANNED_DOMAINS = {
    "code_rust": "follow-up code track",
    "math_lean4": "deferred until math track goes live (Lean kernel terms, not tree-sitter)",
}


def fingerprint_match_score(statement_formal: str, domain: str, corpus_index_path: str) -> float:
    """Structural fingerprint contamination signal. Returns [0, 1]; higher = match in corpus.

    Math (Lean 4): alpha-equivalent normalization of the proof term, hash, lookup.
    Code: tree-sitter parse, canonicalization (rename locals, normalize literals, strip
    comments and whitespace), hash, lookup. Catches alpha-renamed and reformatted lifts
    that defeat n-gram and LSH.

    Launch scope is Python only. Other domains return 0.0 (no signal); the layered
    orchestrator falls back to n-gram + LSH + embedding for unsupported domains.
    """
    if domain not in SUPPORTED_DOMAINS_AT_LAUNCH:
        bt.logging.warning(
            f"ast_fingerprint: domain {domain!r} not supported at launch; returning 0.0"
        )
        return 0.0

    bt.logging.warning(f"ast_fingerprint.fingerprint_match_score stubbed (domain={domain})")
    return 0.0
