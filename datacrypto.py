import base64
import gzip
import io
from Crypto.Cipher import AES
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.backends import default_backend
import hashlib

def sha1_digest(data):
    return hashlib.sha1(data).digest()

def get_aes_key_from_string(password):
    # Generate SHA-1 hash of the password
    sha1_hash = sha1_digest(password)
    # Use first 16 bytes (128 bits) of the SHA-1 hash as the AES key
    return sha1_hash[:16]

def aes_decrypt(encrypted_data, key):
    # Initialize cipher
    cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
    decryptor = cipher.decryptor()

    # Perform decryption
    decrypted_padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
    #print(decrypted_padded_data)
    # Unpad the decrypted data
    unpadder = PKCS7(algorithms.AES.block_size).unpadder()

    data = unpadder.update(decrypted_padded_data) + unpadder.finalize()

    return data

def decompress_data(data):
    buffer = io.BytesIO(data)
    with gzip.GzipFile(fileobj=buffer, mode='rb') as f:
        return f.read()

def decrypt_request_body(encrypted_data_base64, key=""):
    # Step 1: Decode the encrypted data from Base64
    encrypted_data = base64.b64decode(encrypted_data_base64)

    #print (encrypted_data)
    # Step 2: Derive the AES key from the provided key string
    aeskey = get_aes_key_from_string(key.encode('utf-8'))
    #print(aeskey)
    # Step 3: Decrypt the encrypted data using AES
    decrypted_data = aes_decrypt(encrypted_data, aeskey)

    # Step 4: Decompress the decrypted data
    decompressed_data = decompress_data(decrypted_data)

    return decompressed_data


import requests
import base64
import json
from Crypto.Cipher import AES
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7
import hashlib


def sha1_digest(data):
    return hashlib.sha1(data).digest()


def get_aes_key_from_string(password):
    # Generate SHA-1 hash of the password
    sha1_hash = sha1_digest(password)
    # Use first 16 bytes (128 bits) of the SHA-1 hash as the AES key
    return sha1_hash[:16]


def aes_encrypt(data, key):
    # Pad the data to be a multiple of the block size
    padder = PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(data) + padder.finalize()

    # Initialize cipher
    cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
    encryptor = cipher.encryptor()

    # Perform encryption
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    return encrypted_data



def encrypt_request_body(data, key=""):
    # Step 1: Compress the data using GZIP
    compressed_data = compress_data(data)

    # Step 2: Encrypt the compressed data using AES
    # cipher = AES.new(key.encode('utf-8'), AES.MODE_ECB)
    # encrypted_data = cipher.encrypt(pad(compressed_data))
    a = compressed_data  # Replace with your actual data
    str_input = key  # Replace with your actual password
    aeskey = get_aes_key_from_string(str_input.encode('utf-8'))
    encrypted_data = aes_encrypt(a, aeskey)
    # Step 3: Encode the encrypted data to Base64
    return base64.b64encode(encrypted_data)



def compress_data(data):
    import gzip
    import io
    buffer = io.BytesIO()
    with gzip.GzipFile(fileobj=buffer, mode='wb') as f:
        f.write(data)
    return buffer.getvalue()


def pad(data):
    # PKCS5 Padding
    padding_len = AES.block_size - len(data) % AES.block_size
    padding = chr(padding_len).encode('utf-8') * padding_len
    return data + padding


def build_data():
    data = {
        
    }

    # Convert data dictionary to JSON string and then to bytes
    json_data = json.dumps(data).encode('utf-8')

    # Encrypt the data using the provided key
    #key = getHandleKey()  # 获取加密密钥
    encrypted_data = encrypt_request_body(json_data)
    return encrypted_data

