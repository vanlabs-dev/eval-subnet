from typing import List, Optional, TypedDict
import os
import httpx
import bittensor as bt


CHUTES_API_KEY = os.environ.get("CHUTES_API_KEY")
CHUTES_BASE_URL = os.environ.get("CHUTES_BASE_URL", "https://api.chutes.ai")
DEFAULT_BUDGET_SEC = 300


# Display names. Resolved to Chutes endpoint IDs at call time by the
# integration layer. Verify availability against the live SN64 chute
# inventory before any real implementation; vendor IDs and Chutes slugs
# differ from these human-readable names.
FLAGSHIP_MODELS = [
    "Claude Opus 4.7",
    "GPT-5.3 Codex",
    "Gemini 3.1 Pro",
]
ELDER_MODELS = [
    "Claude Sonnet 3.5",
    "GPT-4o",
    "Gemini 1.5 Pro",
]
DEFAULT_PANEL = FLAGSHIP_MODELS + ELDER_MODELS


# Approximate training cutoffs per model. Update on panel rotation; the value
# is recorded with each accepted problem so historical scoring stays auditable
# even after vendor cutoff revisions. Verify against vendor model cards.
MODEL_CUTOFFS = {
    "Claude Opus 4.7": "2026-Q1",
    "GPT-5.3 Codex": "2025-Q4",
    "Gemini 3.1 Pro": "2026-Q1",
    "Claude Sonnet 3.5": "2024-Q2",
    "GPT-4o": "2023-Q4",
    "Gemini 1.5 Pro": "2024-Q2",
}


class PanelResult(TypedDict):
    panel: List[str]
    results: List[bool]
    cutoffs: List[str]
    epoch_pinned: Optional[int]


async def panel_inference(
    statement: str,
    panel: Optional[List[str]] = None,
    budget_sec: int = DEFAULT_BUDGET_SEC,
    epoch: Optional[int] = None,
) -> PanelResult:
    """Run a fixed panel of frontier and elder models against the candidate statement.

    Returns a pinned snapshot recording the exact panel composition and per-model
    training cutoffs at call time, so later audits can verify which panel a problem
    was scored against. Panel rotates on subnet governance vote; the snapshot is
    what defends against drift.

    Panel entries are display names; the real implementation resolves them to
    Chutes endpoint IDs at call time.
    """
    panel = panel if panel is not None else DEFAULT_PANEL
    cutoffs = [MODEL_CUTOFFS.get(m, "unknown") for m in panel]

    if CHUTES_API_KEY is None:
        bt.logging.warning("CHUTES_API_KEY not set; panel inference stubbed all-fail")
        return {
            "panel": panel,
            "results": [False] * len(panel),
            "cutoffs": cutoffs,
            "epoch_pinned": epoch,
        }

    bt.logging.warning("chutes.panel_inference stubbed")
    return {
        "panel": panel,
        "results": [False] * len(panel),
        "cutoffs": cutoffs,
        "epoch_pinned": epoch,
    }


def frontier_failrate(panel_result: PanelResult) -> float:
    results = panel_result.get("results", [])
    if not results:
        return 0.0
    return 1.0 - (sum(results) / len(results))
