from typing import List
import os
import httpx
import bittensor as bt


CHUTES_API_KEY = os.environ.get("CHUTES_API_KEY")
CHUTES_BASE_URL = os.environ.get("CHUTES_BASE_URL", "https://api.chutes.ai")
DEFAULT_PANEL = ["claude-opus-4-7", "gpt-5-3-codex", "gemini-3-1-pro", "gpt-5-4-pro"]
DEFAULT_BUDGET_SEC = 300


async def panel_inference(
    statement: str,
    panel: List[str] = DEFAULT_PANEL,
    budget_sec: int = DEFAULT_BUDGET_SEC,
) -> List[bool]:
    if CHUTES_API_KEY is None:
        bt.logging.warning("CHUTES_API_KEY not set; panel inference stubbed all-fail")
        return [False] * len(panel)

    bt.logging.warning("chutes.panel_inference stubbed")
    return [False] * len(panel)


def frontier_failrate(panel_results: List[bool]) -> float:
    if not panel_results:
        return 0.0
    return 1.0 - (sum(panel_results) / len(panel_results))
