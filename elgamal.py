import random

from params import p
from params import g


def keygen():
    sk = random.randint(1, (p - 1)/2)
    pk = pow(g, sk, p)
    return pk, sk


def encrypt(pk, m):
    r = random.randint(1, (p - 1)/2)
    c1 = pow(g, r, p)
    c2 = (pow(pk, r, p) * m) % p
    return [c1, c2]


def decrypt(sk, c):
    c1 = c[0]
    c2 = c[1]
    m = (pow(c1, -sk, p) * (c2 % p)) % p
    return m

