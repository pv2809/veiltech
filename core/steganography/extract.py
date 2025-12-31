from steganography.constants import STEGO_SIGNATURE
from hashlib import sha256

def extract_payload(raw_bytes: bytes):
    if not raw_bytes.startswith(STEGO_SIGNATURE):
        raise ValueError("No VeilTech data found (image destroyed or not protected)")

    payload = raw_bytes[len(STEGO_SIGNATURE):]

    stored_hash = payload[:32]       # SHA-256 = 32 bytes
    secret = payload[32:]

    calculated_hash = sha256(secret).digest()

    if stored_hash != calculated_hash:
        raise ValueError("Tampering detected")

    return secret
