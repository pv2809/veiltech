from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64

KEY_SIZE = 32  # 256-bit AES key


def generate_key() -> bytes:
    """Generate a secure random AES key"""
    return get_random_bytes(KEY_SIZE)


def encrypt_data(plain_text: str, key: bytes) -> dict:
    """
    Encrypt data using AES-GCM.
    Returns ciphertext, nonce, and tag.
    """
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(plain_text.encode("utf-8"))

    return {
        "ciphertext": base64.b64encode(ciphertext).decode("utf-8"),
        "nonce": base64.b64encode(cipher.nonce).decode("utf-8"),
        "tag": base64.b64encode(tag).decode("utf-8"),
    }


def decrypt_data(encrypted: dict, key: bytes) -> str:
    """
    Decrypt AES-GCM encrypted data.
    Raises error if data is tampered.
    """
    cipher = AES.new(
        key,
        AES.MODE_GCM,
        nonce=base64.b64decode(encrypted["nonce"])
    )

    plaintext = cipher.decrypt_and_verify(
        base64.b64decode(encrypted["ciphertext"]),
        base64.b64decode(encrypted["tag"])
    )

    return plaintext.decode("utf-8")
