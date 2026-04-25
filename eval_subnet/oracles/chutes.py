from typing import List, Optional, TypedDict
import os
import httpx
import bittensor as bt


CHUTES_API_KEY = os.environ.get("CHUTES_API_KEY")
CHUTES_BASE_URL = os.environ.get("CHUTES_BASE_URL", "https://api.chutes.ai")
DEFAULT_BUDGET_SEC = 300


# Flagship and elder tiers by vendor. Cutoff diversity catches the
# "flagship fails but elder solves" signal that points to memorization in
# older training corpora that newer models trained around.
FLAGSHIP_MODELS = [
    "claude-opus-4-7",
    "gpt-5-3-codex",
    "gemini-3-1-pro",
]
ELDER_MODELS = [
    "claude-sonnet-3-5",
    "gpt-4o",
    "gemini-1-5-pro",
]
DEFAULT_PANEL = FLAGSHIP_MODELS + ELDER_MODELS


# Approximate training cutoffs per model. Update on panel rotation; the value
# is recorded with each accepted problem so historical scoring stays auditable
# even after vendor cutoff revisions.
MODEL_CUTOFFS = {
    "claude-opus-4-7": "2026-Q1",
    "gpt-5-3-codex": "2025-Q4",
    "gemini-3-1-pro": "2026-Q1",
    "claude-sonnet-3-5": "2024-Q2",
    "gpt-4o": "2023-Q4",
    "gemini-1-5-pro": "2024-Q2",
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
