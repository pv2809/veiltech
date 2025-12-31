from crypto_pin import encrypt_file, decrypt_file
from stego_lsb import embed_bytes, extract_bytes

STEGO_SIGNATURE = b"VEILTECH::STEGO::v1"


def has_veiltech_signature(data: bytes) -> bool:
    return data.startswith(STEGO_SIGNATURE)


# ------------------ ENCRYPT & EMBED ------------------

PIN = input("Enter PIN: ")

encrypt_file(
    input_path="secret.txt",
    pin=PIN,
    output_path="encrypted.json",
    expires_in_seconds=180,   # 3 minutes
    max_views=1,
    view_only=True
)

with open("encrypted.json", "rb") as f:
    encrypted_bytes = f.read()

# ✅ prepend signature
payload_bytes = STEGO_SIGNATURE + encrypted_bytes

embed_bytes(
    image_path="input.jpg",
    payload_bytes=payload_bytes,
    output_path="carrier.png"
)

print("✅ Encrypted data hidden inside image")


# ------------------ EXTRACT & REVEAL ------------------

try:
    extracted_bytes = extract_bytes("carrier.png")

    if not has_veiltech_signature(extracted_bytes):
        raise ValueError("❌ No VeilTech data found (image destroyed or not protected)")

    # ✅ remove signature
    clean_payload = extracted_bytes[len(STEGO_SIGNATURE):]

    with open("extracted.json", "wb") as f:
        f.write(clean_payload)

    print("✅ Data extracted from image")

    pin_check = input("Enter PIN to reveal: ")

    payload = decrypt_file("extracted.json", pin_check)

    print("📄 Filename:", payload["filename"])
    print("👁 View-only:", payload["view_only"])
    print("🔢 Views used:", payload["used_views"])

    file_bytes = bytes.fromhex(payload["file_hex"])

    with open("revealed.txt", "wb") as f:
        f.write(file_bytes)

    print("✅ File revealed")

except ValueError as e:
    print(e)
