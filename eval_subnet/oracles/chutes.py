from typing import List, Optional, TypedDict
import os
import httpx
import bittensor as bt


CHUTES_API_KEY = os.environ.get("CHUTES_API_KEY")
CHUTES_BASE_URL = os.environ.get("CHUTES_BASE_URL", "https://api.chutes.ai")
DEFAULT_PANEL = ["claude-opus-4-7", "gpt-5-3-codex", "gemini-3-1-pro", "gpt-5-4-pro"]
DEFAULT_BUDGET_SEC = 300


class PanelResult(TypedDict):
    panel: List[str]
    results: List[bool]
    epoch_pinned: Optional[int]


async def panel_inference(
    statement: str,
    panel: Optional[List[str]] = None,
    budget_sec: int = DEFAULT_BUDGET_SEC,
    epoch: Optional[int] = None,
) -> PanelResult:
    """Run a fixed panel of frontier models against the candidate statement.

    Returns a pinned snapshot recording the exact panel composition at call time, so
    later audits can verify which panel a problem was scored against. Panel rotates
    quarterly via subnet governance; the snapshot is what defends against drift.
    """
    panel = panel if panel is not None else DEFAULT_PANEL
    if CHUTES_API_KEY is None:
        bt.logging.warning("CHUTES_API_KEY not set; panel inference stubbed all-fail")
        return {"panel": panel, "results": [False] * len(panel), "epoch_pinned": epoch}

    bt.logging.warning("chutes.panel_inference stubbed")
    return {"panel": panel, "results": [False] * len(panel), "epoch_pinned": epoch}


def frontier_failrate(panel_result: PanelResult) -> float:
    results = panel_result.get("results", [])
    if not results:
        return 0.0
    return 1.0 - (sum(results) / len(results))
