import base64


def encode_ml(data: str) -> str:
    """
    Encoder function (ML placeholder).

    This simulates an encoder by:
    1. Reversing the string (transformation)
    2. Base64 encoding (obfuscation)

    Later, this can be replaced with a trained ML autoencoder
    without changing the interface.
    """
    transformed = data[::-1]
    encoded = base64.b64encode(transformed.encode("utf-8")).decode("utf-8")
    return encoded


def decode_ml(data: str) -> str:
    """
    Decoder function (ML placeholder).

    This reverses the encoder steps:
    1. Base64 decode
    2. Reverse string back to original
    """
    decoded = base64.b64decode(data.encode("utf-8")).decode("utf-8")
    original = decoded[::-1]
    return original
