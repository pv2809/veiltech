import pytest
import json
import time
from core.pipeline.secure_pipeline import (
    create_secure_image,
    reveal_secure_file
)
from PIL import Image
import os
def test_valid_secure_image(tmp_path):
    cover = "core/tests/assets/cover.jpg"
    output = tmp_path / "carrier.png"

    file_id = "TEST_FILE_001"

    create_secure_image(
        cover_image=cover,
        output_image=str(output),
        file_id=file_id
    )

    extracted_file_id = reveal_secure_file(str(output))
    assert extracted_file_id == file_id
def test_random_image_rejected():
    with pytest.raises(ValueError):
        reveal_secure_file("core/tests/assets/random.jpg")
def test_single_pixel_tamper_detected(tmp_path):
    cover = "core/tests/assets/cover.jpg"
    output = tmp_path / "carrier.png"

    create_secure_image(
        cover_image=cover,
        output_image=str(output),
        file_id="TEST_TAMPER"
    )

    img = Image.open(output)
    pixels = img.load()
    r, g, b = pixels[0, 0]
    pixels[0, 0] = (r ^ 1, g, b)
    img.save(output)

    with pytest.raises(ValueError):
        reveal_secure_file(str(output))

def test_corrupted_payload(tmp_path):
    bad_image = tmp_path / "bad.png"

    img = Image.new("RGB", (100, 100), color="white")
    img.save(bad_image)

    with pytest.raises(ValueError):
        reveal_secure_file(str(bad_image))

    
