import hashlib
from typing import Sequence


def compute_routing_seed(epoch: int, role: bytes, salt: bytes = b"") -> bytes:
    return hashlib.sha256(f"{epoch}".encode() + role + salt).digest()


def stable_sample(seed: bytes, items: Sequence, k: int) -> list:
    if k >= len(items):
        return list(items)
    scored = [
        (int.from_bytes(hashlib.sha256(seed + str(i).encode()).digest()[:8], "big"), x)
        for i, x in enumerate(items)
    ]
    scored.sort()
    return [x for _, x in scored[:k]]


def discriminator_subset_for_epoch(
    epoch: int, all_uids: Sequence[int], k: int, salt: bytes = b""
) -> list:
    seed = compute_routing_seed(epoch, b"discriminator", salt)
    return stable_sample(seed, list(all_uids), k)


def solver_subset_for_problem(
    epoch: int, problem_hash: str, all_uids: Sequence[int], k: int, salt: bytes = b""
) -> list:
    role = b"solver:" + problem_hash.encode()
    seed = compute_routing_seed(epoch, role, salt)
    return stable_sample(seed, list(all_uids), k)


def commit_routing_salt(epoch: int, salt: bytes) -> bytes:
    """Validator publishes this hash on-chain at epoch start; reveals `salt` after the
    submission window closes. Generators cannot predict the routing while they submit
    because they do not know `salt` until reveal.
    """
    return hashlib.sha256(f"{epoch}".encode() + salt).digest()
