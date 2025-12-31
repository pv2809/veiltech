from PIL import Image
import math

STEGO_SIGNATURE = b"VEILTECH::STEGO::v1"

def _bytes_to_bits(data: bytes):
    for byte in data:
        for i in range(7, -1, -1):
            yield (byte >> i) & 1


def _bits_to_bytes(bits):
    result = bytearray()
    byte = 0
    count = 0

    for bit in bits:
        byte = (byte << 1) | bit
        count += 1

        if count == 8:
            result.append(byte)
            byte = 0
            count = 0

    return bytes(result)


def embed_bytes(
    image_path: str,
    payload: bytes,
    output_path: str
):
    image = Image.open(image_path).convert("RGB")
    pixels = list(image.getdata())

    payload_len = len(payload)
    header = payload_len.to_bytes(4, "big")
    full_payload = STEGO_SIGNATURE+ header + payload

    bits = list(_bytes_to_bits(full_payload))
    max_capacity = len(pixels) * 3

    if len(bits) > max_capacity:
        raise ValueError("Payload too large for image")

    new_pixels = []
    bit_index = 0

    for r, g, b in pixels:
        if bit_index < len(bits):
            r = (r & ~1) | bits[bit_index]
            bit_index += 1
        if bit_index < len(bits):
            g = (g & ~1) | bits[bit_index]
            bit_index += 1
        if bit_index < len(bits):
            b = (b & ~1) | bits[bit_index]
            bit_index += 1

        new_pixels.append((r, g, b))

    image.putdata(new_pixels)
    image.save(output_path)


def extract_bytes(image_path: str) -> bytes:
    image = Image.open(image_path).convert("RGB")
    pixels = list(image.getdata())

    bits = []
    for r, g, b in pixels:
        bits.append(r & 1)
        bits.append(g & 1)
        bits.append(b & 1)

    raw = _bits_to_bytes(bits)

    # 🔐 7.5.1 — Origin verification
    if not raw.startswith(STEGO_SIGNATURE):
        raise ValueError("NOT_VEILTECH_IMAGE")

    offset = len(STEGO_SIGNATURE)

    # 🔐 7.5.2 — Payload length extraction
    if len(raw) < offset + 4:
        raise ValueError("CORRUPTED_PAYLOAD")

    payload_len = int.from_bytes(
        raw[offset:offset + 4],
        "big"
    )

    payload_start = offset + 4
    payload_end = payload_start + payload_len

    # 🔐 7.5.3 — Integrity check
    if payload_end > len(raw):
        raise ValueError("CORRUPTED_PAYLOAD")

    return raw[payload_start:payload_end]
