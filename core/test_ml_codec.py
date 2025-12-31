from core.ml_codec import encode_ml, decode_ml

original = "VeilTech ML Layer Test"

encoded = encode_ml(original)
decoded = decode_ml(encoded)

print("Original:", original)
print("Encoded :", encoded)
print("Decoded :", decoded)
