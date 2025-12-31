from core.crypto_utils import generate_key
from core.core_pipeline import protect_data, reveal_data

key = generate_key()

original_text = "VeilTech Hybrid Core Test"

protected = protect_data(original_text, key)
revealed = reveal_data(protected, key)

print("Original :", original_text)
print("Protected:", protected)
print("Revealed :", revealed)
