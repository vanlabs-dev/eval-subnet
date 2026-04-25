import os
import shutil
import subprocess
import tempfile
import bittensor as bt


LEAN_BIN = shutil.which("lean")
DEFAULT_TIMEOUT_SEC = 60
TOOLCHAIN_FILE = "lean-toolchain"


def required_lean_version() -> str | None:
    """Read the pinned Lean toolchain spec from the repo root.

    Validators MUST run the same Lean version. Different versions produce
    different typecheck behavior and break ground-truth consistency across
    the validator set.
    """
    here = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    path = os.path.join(here, TOOLCHAIN_FILE)
    if not os.path.exists(path):
        return None
    return open(path, encoding="utf-8").read().strip()


def verify_toolchain() -> bool:
    """Return True if the running `lean` matches the pinned toolchain.

    Logs a warning and returns False otherwise. Real validators should refuse
    to start if this check fails.
    """
    if LEAN_BIN is None:
        return False
    pinned = required_lean_version()
    if pinned is None:
        bt.logging.warning("lean-toolchain file missing; cannot verify version")
        return False
    try:
        result = subprocess.run([LEAN_BIN, "--version"], capture_output=True, text=True, timeout=10)
        running = result.stdout.strip()
    except Exception as e:
        bt.logging.error(f"lean --version failed: {e}")
        return False
    pinned_marker = pinned.split(":")[-1]
    if pinned_marker not in running:
        bt.logging.warning(f"lean version mismatch: running {running!r}, pinned {pinned!r}")
        return False
    return True


def typecheck(statement_formal: str, formal_solution: str, timeout: int = DEFAULT_TIMEOUT_SEC) -> bool:
    if LEAN_BIN is None:
        bt.logging.warning("lean not on PATH; typecheck stubbed False")
        return False

    source = f"{statement_formal}\n\n{formal_solution}\n"
    with tempfile.NamedTemporaryFile("w", suffix=".lean", delete=False) as f:
        f.write(source)
        path = f.name

    try:
        result = subprocess.run(
            [LEAN_BIN, path],
            capture_output=True,
            timeout=timeout,
            text=True,
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        bt.logging.warning(f"lean typecheck timed out after {timeout}s")
        return False
    except Exception as e:
        bt.logging.error(f"lean typecheck error: {e}")
        return False
