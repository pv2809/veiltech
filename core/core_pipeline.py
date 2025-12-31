from core.ml_codec import encode_ml, decode_ml
from core.crypto_utils import encrypt_data, decrypt_data


def protect_data(plain_text: str, aes_key: bytes) -> dict:
    """
    Full protection pipeline:
    ML Encode -> AES Encrypt
    """
    # 1. ML encoder (obfuscation layer)
    encoded = encode_ml(plain_text)

    # 2. AES encryption (security layer)
    encrypted_payload = encrypt_data(encoded, aes_key)

    return encrypted_payload


def reveal_data(encrypted_payload: dict, aes_key: bytes) -> str:
    """
    Full reveal pipeline:
    AES Decrypt -> ML Decode
    """
    # 1. AES decryption
    decrypted_encoded = decrypt_data(encrypted_payload, aes_key)

    # 2. ML decoder (restore original)
    original_text = decode_ml(decrypted_encoded)

    return original_text
