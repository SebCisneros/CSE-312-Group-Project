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
