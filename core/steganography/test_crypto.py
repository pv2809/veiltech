from crypto_pin import encrypt_file, decrypt_file

pin = input("Enter PIN: ")

encrypt_file(
    input_path="secret.txt",
    pin=pin,
    output_path="encrypted.json"
)

print("✅ File encrypted")

pin_check = input("Enter PIN to decrypt: ")

decrypt_file(
    encrypted_path="encrypted.json",
    pin=pin_check,
    output_path="revealed.txt"
)

print("✅ File decrypted")
