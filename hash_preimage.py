import hashlib
import os


def hash_preimage(target_string):
    if not all([x in '01' for x in target_string]):
        print("Input should be a string of bits")
        return
    while True:
        nonce = os.urandom(200)
        nonce_hash = bin(int(hashlib.sha256(nonce).hexdigest(), 16))
        if nonce_hash == target_string:
            continue
        elif nonce_hash[-len(target_string):] == target_string:
            return nonce
