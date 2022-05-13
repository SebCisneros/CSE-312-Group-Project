import socketserver
import hashlib
import base64
import json


def compute_accept(key):
    guid = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
    to_hash = (key + guid).encode()
    hash_bytes = hashlib.sha1(to_hash).digest()
    encode_hash = base64.b64encode(hash_bytes)
    return encode_hash.decode()


def generate_frame(payload_bytes):
    # TODO: Does not handle larger messages > 125 bytes
    payload_length = len(payload_bytes)
    frame = b'\x81'  # first byte is 1000 0001 to send a text frame
    if payload_length < 126:
        frame = frame + payload_length.to_bytes(1, 'big')
    elif payload_length < 65536:
        # 0111 1110
        frame = frame + b'\x7e' + payload_length.to_bytes(2, 'big')
    else:
        # 0111 1111
        frame = frame + b'\x7f' + payload_length.to_bytes(8, 'big')

    frame = frame + payload_bytes
    return frame
