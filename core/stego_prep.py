import json
import struct


def prepare_for_stego(encrypted_payload: dict) -> bytes:
    """
    Prepares encrypted data for steganographic embedding.

    Steps:
    1. Convert encrypted dict to JSON bytes
    2. Add 4-byte length header
    3. Return final byte stream
    """
    # Convert dict to JSON bytes
    json_bytes = json.dumps(encrypted_payload).encode("utf-8")

    # Pack length of JSON (4 bytes, big-endian)
    length_header = struct.pack(">I", len(json_bytes))

    # Final byte stream
    return length_header + json_bytes


def extract_from_stego(byte_stream: bytes) -> dict:
    """
    Extracts encrypted payload from steganographic byte stream.
    """
    # Read first 4 bytes to get length
    length = struct.unpack(">I", byte_stream[:4])[0]

    # Extract JSON payload
    json_bytes = byte_stream[4:4 + length]

    return json.loads(json_bytes.decode("utf-8"))
