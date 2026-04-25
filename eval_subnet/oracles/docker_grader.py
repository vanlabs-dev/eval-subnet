import shutil
import bittensor as bt


DOCKER_BIN = shutil.which("docker")
DEFAULT_TIMEOUT_SEC = 600


def run_grader(grader_image_hash: str, solution: str, timeout: int = DEFAULT_TIMEOUT_SEC) -> bool:
    if DOCKER_BIN is None:
        bt.logging.warning("docker not on PATH; grader stubbed False")
        return False
    bt.logging.warning(f"docker_grader.run_grader stubbed (image={grader_image_hash[:12]})")
    return False
