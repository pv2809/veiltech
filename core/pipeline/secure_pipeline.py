import json
import time
from core.steganography.stego_lsb import embed_bytes, extract_bytes
from PIL import Image
import hashlib

STEGO_SIGNATURE = b"VEILTECH::SECURE::v1::"
MAX_ABSOLUTE_PAYLOAD = 5 * 1024 * 1024

def compute_stego_capacity(image_path: str) -> int:
    img = Image.open(image_path)
    width, height = img.size

    max_capacity = (width * height * 3) // 8
    usable_capacity = max_capacity - 512  # safety buffer

    return min(usable_capacity, MAX_ABSOLUTE_PAYLOAD)

def compute_image_fingerprint(image_path: str) -> str:
    img = Image.open(image_path).convert("RGB")
    pixels = img.load()

    width, height = img.size
    clean_bytes = bytearray()

    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            # zero out LSBs
            clean_bytes.extend([
                r & 0b11111110,
                g & 0b11111110,
                b & 0b11111110
            ])

    return hashlib.sha256(bytes(clean_bytes)).hexdigest()
def create_secure_image(
    cover_image: str,
    output_image: str,
    file_id: str
):
    fingerprint = compute_image_fingerprint(cover_image)

    payload = {
        "veiltech": "v1",
        "file_id": file_id,
        "image_fingerprint": fingerprint,
        "created_at": time.time()
    }

    raw_payload = STEGO_SIGNATURE + json.dumps(payload).encode()

    embed_bytes(
        image_path=cover_image,
        payload=raw_payload,
        output_path=output_image
    )

    print("✅ Secure image created:", output_image)
def reveal_secure_file(carrier_image: str) -> str:
    raw = extract_bytes(carrier_image)

    # 1️⃣ Signature check
    if not raw.startswith(STEGO_SIGNATURE):
        raise ValueError("NOT_VEILTECH_IMAGE")

    raw = raw[len(STEGO_SIGNATURE):]

    # 2️⃣ Parse payload
    try:
        extracted = json.loads(raw.decode())
    except Exception:
        raise ValueError("CORRUPTED_PAYLOAD")

    if extracted.get("veiltech") != "v1":
        raise ValueError("INVALID_VEILTECH_VERSION")

    # 3️⃣ Fingerprint verification
    current_fp = compute_image_fingerprint(carrier_image)

    if extracted["image_fingerprint"] != current_fp:
        raise ValueError("IMAGE_TAMPERED")

    return extracted["file_id"]

def extract_file_id(carrier_image: str) -> str:
    raw = extract_bytes(carrier_image)

    if not raw.startswith(STEGO_SIGNATURE):
        raise ValueError("NOT_VEILTECH_IMAGE")

    payload = json.loads(raw[len(STEGO_SIGNATURE):].decode())
    return payload["file_id"]


