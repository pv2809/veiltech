import time
import json
import hashlib
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

KEY_LENGTH = 32
PBKDF2_ITERATIONS = 200_000


def derive_key(pin: str, salt: bytes) -> bytes:
    return PBKDF2(pin.encode(), salt, dkLen=KEY_LENGTH, count=PBKDF2_ITERATIONS)


def encrypt_file(
    input_path: str,
    pin: str,
    output_path: str,
    expires_in_seconds: int = 180,
    max_views: int = 1,
    view_only: bool = True
):
    with open(input_path, "rb") as f:
        file_bytes = f.read()

    payload = {
        "filename": input_path,
        "created_at": int(time.time()),
        "expires_at": int(time.time()) + expires_in_seconds,
        "max_views": max_views,
        "used_views": 0,
        "view_only": view_only,
        "file_hex": file_bytes.hex()
    }

    payload_bytes = json.dumps(payload).encode()
    integrity_hash = hashlib.sha256(payload_bytes).digest()

    salt = get_random_bytes(16)
    iv = get_random_bytes(16)
    key = derive_key(pin, salt)

    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(payload_bytes, AES.block_size))

    encrypted = {
        "salt": salt.hex(),
        "iv": iv.hex(),
        "ciphertext": ciphertext.hex(),
        "hash": integrity_hash.hex()
    }

    with open(output_path, "w") as f:
        json.dump(encrypted, f)


def decrypt_file(encrypted_path: str, pin: str):
    with open(encrypted_path, "r") as f:
        encrypted = json.load(f)

    salt = bytes.fromhex(encrypted["salt"])
    iv = bytes.fromhex(encrypted["iv"])
    ciphertext = bytes.fromhex(encrypted["ciphertext"])
    expected_hash = bytes.fromhex(encrypted["hash"])

    key = derive_key(pin, salt)
    cipher = AES.new(key, AES.MODE_CBC, iv)

    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)

    if hashlib.sha256(plaintext).digest() != expected_hash:
        raise ValueError("❌ Tampering detected")

    payload = json.loads(plaintext.decode())
    now = int(time.time())

    if now > payload["expires_at"]:
        raise ValueError("❌ File expired")

    if payload["used_views"] >= payload["max_views"]:
        raise ValueError("❌ Access limit exceeded")

    payload["used_views"] += 1
    return payload
