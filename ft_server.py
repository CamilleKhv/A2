import socket
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
import os

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 65433
FILE_TO_SEND = "file_to_transfer.txt"  # File that will be encrypted and sent

"""
A file that implements secure key exchange and encrypted file transfer.

Attributes:

Methods:
- load_private_key(): Loads the server's private RSA key.
- setup_server(): Configures and starts the server.
- handle_client(): Manages communication with the client.
- exchange_keys(): Exchanges RSA-encrypted AES keys.
- encrypt_and_send_file(): Encrypts and sends a file securely.
"""

def load_private_key(filename):
    """Loads the server's private RSA key from a file."""
    with open(filename, "rb") as key_file:
        return RSA.import_key(key_file.read())

def setup_server():
    """Configures and starts the server."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen()
    print(f"Server listening on {SERVER_HOST} {SERVER_PORT}...")
    return server_socket

def handle_client(client_socket, private_key):
    """Handles communication with a client."""
    
    # Receive the client's public key
    client_public_key = RSA.import_key(client_socket.recv(2048))
    print("Client's public key received.")

    # Generate and send AES key
    aes_key = exchange_keys(client_socket, client_public_key)

    # Encrypt and send a file securely
    encrypt_and_send_file(client_socket, aes_key)

    client_socket.close()

def exchange_keys(client_socket, client_public_key):
    """Generates and sends an AES key encrypted with the client's public key."""
    
    # Generate AES key
    aes_key = os.urandom(32)

    # Encrypt AES key with client's public key
    rsa_cipher = PKCS1_OAEP.new(client_public_key)
    encrypted_aes_key = rsa_cipher.encrypt(aes_key)

    # Send the encrypted AES key
    client_socket.send(encrypted_aes_key)
    print("AES key sent.")
    
    return aes_key

def encrypt_and_send_file(client_socket, aes_key):
    """Encrypts a file with AES-GCM and sends it to the client."""

    # Read the file in binary mode
    with open(FILE_TO_SEND, "rb") as f:
        plaintext = f.read()

    # Create AES-GCM cipher
    cipher_aes = AES.new(aes_key, AES.MODE_GCM) 
    nonce = cipher_aes.nonce  # Nonce is required for AES-GCM
    
    # Encrypt the file and get the authentication tag
    ciphertext, tag = cipher_aes.encrypt_and_digest(plaintext)

    # Send nonce first (needed for decryption)
    client_socket.send(nonce)
    print("Nonce sent.")

    # Send authentication tag
    client_socket.send(tag)  # AES-GCM requires sending tag separately
    print("Tag sent.")

    # Send the encrypted file size first (to handle large files properly)
    client_socket.send(len(ciphertext).to_bytes(4, 'big'))

    # Send encrypted file
    client_socket.sendall(ciphertext)
    print("Encrypted file sent.")

"""Main entry point of the server."""
private_key = load_private_key("server_private.pem")
server_socket = setup_server()

while True:  # Allows handling multiple connections
    client_socket, client_address = server_socket.accept()
    print(f"Client connected: {client_address}")
    handle_client(client_socket, private_key)
