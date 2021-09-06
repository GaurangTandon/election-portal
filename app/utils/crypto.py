from app.models.models import Hashes
import hashlib
import secrets
from typing import List, Union


def generate_nonce(length=Hashes.NONCE_LEN) -> str:
    """
    Generate a random hexadecimal number with
    `length` digits
    """
    return secrets.token_hex(length // 2)


def hash256(iterable: Union[List[bytes], str]) -> str:
    if isinstance(iterable, list):
        serialized = b",".join(iterable)
    else:
        serialized = iterable.encode()
    return hashlib.sha256(serialized).hexdigest()


def get_nonce_and_hash(keys: str):
    nonce = generate_nonce()
    final_hash = hash256([keys.encode(), nonce.encode()])
    return nonce, final_hash
