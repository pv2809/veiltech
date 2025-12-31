from steganography.constants import STEGO_SIGNATURE

def prepare_payload(secret_bytes: bytes, integrity_hash: bytes) -> bytes:
    """
    Payload structure:
    [SIGNATURE][HASH][SECRET]
    """
    return STEGO_SIGNATURE + integrity_hash + secret_bytes
