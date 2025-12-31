from core.stego_prep import prepare_for_stego, extract_from_stego

sample_encrypted = {
    "ciphertext": "cipher_data_here",
    "nonce": "nonce_here",
    "tag": "tag_here"
}

packed = prepare_for_stego(sample_encrypted)
unpacked = extract_from_stego(packed)

print("Original :", sample_encrypted)
print("Recovered:", unpacked)
