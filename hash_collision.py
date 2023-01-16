import hashlib
import os


def hash_collision(k):
    if not isinstance(k, int):
        print("hash_collision expects an integer")
        return b'\x00', b'\x00'
    if k < 0:
        print("Specify a positive number of bits")
        return b'\x00', b'\x00'

    # Collision finding code goes here
    while True:
        x = os.urandom(200)
        y = os.urandom(200)
        if x == y:
            continue
        x_hash = bin(int(hashlib.sha256(x).hexdigest(), 16))
        y_hash = bin(int(hashlib.sha256(y).hexdigest(), 16))

        if x_hash[-k:] == y_hash[-k:]:
            return x, y


# if __name__ == '__main__':
#     print(hash_collision(5))
