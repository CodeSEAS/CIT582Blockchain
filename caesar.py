def encrypt(key,plaintext):
    ciphertext=""
    #YOUR CODE HERE
    for c in plaintext:
        # all characters are in upper case
        trans_c_number = (key + ord(c) - 65) % 26 + 65
        ciphertext += chr(trans_c_number)
    return ciphertext


def decrypt(key,ciphertext):
    plaintext=""
    #YOUR CODE HERE
    for c in ciphertext:
        # all characters are in upper case
        trans_c_number = (ord(c) - 65 - key) % 26 + 65
        plaintext += chr(trans_c_number)
    return plaintext
#
#
# if __name__ == "__main__":
#     print(encrypt(-1, "ABCD"))
#     print(decrypt(-1, "ZABC"))
