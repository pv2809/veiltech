STEGO_SIGNATURE = b"VEILTECH::STEGO::v1"

def has_veiltech_signature(data: bytes) -> bool:
    return data.startswith(STEGO_SIGNATURE)
