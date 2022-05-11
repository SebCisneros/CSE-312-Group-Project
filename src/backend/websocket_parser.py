import socketserver
import hashlib
import base64
import json


class WSFrame:

    def __init__(self, frame_bytes):
        self.frame_bytes = frame_bytes
        self.fin = 1
        self.opcode = 0
        self.maskbit = 0

        self.payload_length = 27
        self.payload = b'123456789012345678901234567'
        self.first_mask_or_payload_byte = 0  # what is this?
        self.parse_headers()
        self.parse_payload_length()
        self.finished_buffering = False
        self.check_payload()
        # if self.finished_buffering:
        #     self.extract_payload()

    def print_frame(self):
        for i in range(0, len(self.frame_bytes)):
            the_byte = self.frame_bytes[i]
            # b''.
            print(byte_to_binary_string(the_byte), end='')
            if i % 4 == 3:
                print()

        print("payload length: " + str(self.payload_length))
        print('payload: ' + self.payload.decode())

    def check_payload(self):
        offset = self.first_mask_or_payload_byte
        if self.maskbit == 1:
            offset += 4
        raw_payload = self.frame_bytes[offset:]
        if len(raw_payload) < self.payload_length:
            # still buffering
            return
        else:
            self.finished_buffering = True

    def extract_payload(self):
        # why doing it twice???
        # check_payload()
        offset = self.first_mask_or_payload_byte
        if self.maskbit == 1:
            offset += 4

        raw_payload = self.frame_bytes[offset:]

        if len(raw_payload) < self.payload_length:
            # still buffering
            return
        else:
            self.finished_buffering = True

        if self.maskbit == 1:
            mask = self.frame_bytes[self.first_mask_or_payload_byte: self.first_mask_or_payload_byte + 4]
            payload = b''
            for i in range(self.first_mask_or_payload_byte + 4,
                           self.first_mask_or_payload_byte + 4 + self.payload_length):
                mask_byte_index = (i - self.first_mask_or_payload_byte) % 4
                payload = payload + (self.frame_bytes[i] ^ mask[mask_byte_index]).to_bytes(1, 'little')
            self.payload = payload
        else:
            self.payload = self.frame_bytes[
                           self.first_mask_or_payload_byte: self.first_mask_or_payload_byte + self.payload_length]

    def parse_headers(self):
        self.opcode = self.frame_bytes[0] & 31
        self.fin = self.frame_bytes[0] >> 7
        self.maskbit = self.frame_bytes[1] >> 7

    def parse_payload_length(self):
        first_try = self.frame_bytes[1] & 127

        if first_try < 126:
            self.payload_length = first_try
            self.first_mask_or_payload_byte = 2
        elif first_try == 126:
            payload_length = int(self.frame_bytes[2])
            payload_length = payload_length << 8
            payload_length = payload_length + self.frame_bytes[3]
            self.payload_length = payload_length
            self.first_mask_or_payload_byte = 4
        elif first_try == 127:
            payload_length = int(self.frame_bytes[2])
            for i in range(3, 10):
                print(i)
                print(payload_length)
                print("-----------")
                payload_length = payload_length << 8
                payload_length = payload_length + self.frame_bytes[i]
            self.payload_length = payload_length
            self.first_mask_or_payload_byte = 10
        else:
            print("parsing error")


def byte_to_binary_string(the_byte):
    as_binary = str(bin(the_byte))[2:]
    for i in range(len(as_binary), 8):
        as_binary = '0' + as_binary
    return as_binary
