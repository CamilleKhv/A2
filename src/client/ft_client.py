import socket
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 65433
OUTPUT_FILE = "received_file.txt"  # The decrypted file will be saved as this

"""
A file that implements secure key exchange and encrypted file transfer for the client.

Attributes:

Methods:
- load_private_key(): Loads the client's private RSA key.
- load_public_key(): Loads the client's public RSA key.
- connect_to_server(): Establishes a connection with the server.
- exchange_keys(): Sends public key to server and receives AES key.
- receive_encrypted_file(): Receives and decrypts an encrypted file.
"""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_private_key(filename):
    """Loads the client's private RSA key from a file."""
    key_path = os.path.join(BASE_DIR, filename)
    with open(key_path, "rb") as key_file:
        return RSA.import_key(key_file.read())

def load_public_key(filename):
    """Loads the client's public RSA key from a file."""
    key_path = os.path.join(BASE_DIR, filename)
    with open(key_path, "rb") as key_file:
        return key_file.read()


def connect_to_server():
    """Establishes a connection with the server."""
    print("Connecting to the server...")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))
    print("Connected to server.")
    return client_socket

def exchange_keys(client_socket, private_key):
    """Sends public key to the server and receives the AES key."""
    public_key = load_public_key("client_public.pem")
    client_socket.send(public_key)
    print("Public key sent to server.")

    # Receive and decrypt AES key
    encrypted_aes_key = client_socket.recv(256)
    print(f"AES key received: {len(encrypted_aes_key)} bytes.")

    rsa_cipher = PKCS1_OAEP.new(private_key)
    aes_key = rsa_cipher.decrypt(encrypted_aes_key)
    print("AES key decrypted.")

    return aes_key

def receive_encrypted_file(client_socket, aes_key):
    """Receives and decrypts an encrypted file from the server."""
    nonce = client_socket.recv(16)
    print("Nonce received.")

    tag = client_socket.recv(16)
    print("Tag received.")

    # Receive file size first
    file_size = int.from_bytes(client_socket.recv(4), 'big')

    encrypted_file_data = b""
    while len(encrypted_file_data) < file_size:
        chunk = client_socket.recv(min(4096, file_size - len(encrypted_file_data)))
        if not chunk:
            break
        encrypted_file_data += chunk
    print("Encrypted file received.")

    # Decrypt using AES-GCM
    cipher_aes = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)
    plaintext = cipher_aes.decrypt_and_verify(encrypted_file_data, tag)

    # Save decrypted content to a file
    with open(OUTPUT_FILE, "wb") as f:
        f.write(plaintext)
    print(f"Decrypted file saved as: {OUTPUT_FILE}")

"""Main entry point of the client."""
private_key = load_private_key("client_private.pem")
client_socket = connect_to_server()

aes_key = exchange_keys(client_socket, private_key)
receive_encrypted_file(client_socket, aes_key)

client_socket.close()
