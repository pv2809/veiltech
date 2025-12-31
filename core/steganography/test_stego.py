from stego_lsb import embed_text, extract_text

embed_text(
    image_path="input.jpg",
    secret_text="VeilTech Secret",
    output_path="encoded.png"
)

revealed = extract_text("encoded.png")
print("Revealed:", revealed)
