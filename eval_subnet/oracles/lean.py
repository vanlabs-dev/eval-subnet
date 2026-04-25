import shutil
import subprocess
import tempfile
import bittensor as bt


LEAN_BIN = shutil.which("lean")
DEFAULT_TIMEOUT_SEC = 60


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
