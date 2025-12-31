from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
import os
import base64


PBKDF2_ITERATIONS = 100_000
KEY_LENGTH = 32  # 256-bit key


def derive_key(pin: str, salt: bytes) -> bytes:
    """
    Derive a cryptographic key from a PIN using PBKDF2.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_LENGTH,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    return kdf.derive(pin.encode())


def encrypt_data(data: bytes, pin: str) -> dict:
    """
    Encrypt data using AES-256-GCM with a PIN-derived key.
    """
    salt = os.urandom(16)
    key = derive_key(pin, salt)
    iv = os.urandom(12)  # Recommended size for GCM

    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(iv, data, None)

    return {
        "salt": base64.b64encode(salt).decode(),
        "iv": base64.b64encode(iv).decode(),
        "ciphertext": base64.b64encode(ciphertext).decode(),
    }
def decrypt_data(encrypted: dict, pin: str) -> bytes:
    try:
        salt = base64.b64decode(encrypted["salt"])
        iv = base64.b64decode(encrypted["iv"])
        ciphertext = base64.b64decode(encrypted["ciphertext"])

        key = derive_key(pin, salt)
        aesgcm = AESGCM(key)

        return aesgcm.decrypt(iv, ciphertext, None)
    except Exception:
        raise ValueError("WRONG_PIN")
