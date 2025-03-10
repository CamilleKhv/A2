import socket
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
import os

"""
A file that implements secure key exchange and encrypted file transfer.

Attributes:
SERVER_HOST (str): The server's host IP address.
SERVER_PORT (int): The server's listening port.
FILE_TO_SEND (str): The name of the file to send, which will be encrypted and transferred.

Methods:
- load_private_key(): Loads the server's private RSA key.
- setup_server(): Configures and starts the server.
- handle_client(): Manages communication with the client.
- exchange_keys(): Exchanges RSA-encrypted AES keys.
- encrypt_and_send_file(): Encrypts and sends a file securely.
"""

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 65433
FILE_TO_SEND = "file_to_transfer.txt"
SUPPORTED_ENCRYPTIONS = ["AES-GCM"]  # List of supported encryption methods

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
    encryption_method = perform_handshake(client_socket)
    
    client_public_key = RSA.import_key(client_socket.recv(2048))
    print("Client's public key received.")
    
    aes_key = exchange_keys(client_socket, client_public_key)
    encrypt_and_send_file(client_socket, aes_key)
    client_socket.close()

def perform_handshake(client_socket):
    """Performs handshake to negotiate encryption method."""
    client_supported = client_socket.recv(1024).decode().split(',')
    chosen_method = next((method for method in SUPPORTED_ENCRYPTIONS if method in client_supported), None)
    if not chosen_method:
        raise ValueError("No common encryption method found!")
    client_socket.sendall(chosen_method.encode())
    print(f"Handshake successful. Agreed on encryption: {chosen_method}")
    return chosen_method

def exchange_keys(client_socket, client_public_key):
    """Generates and sends an AES key encrypted with the client's public key."""
    aes_key = os.urandom(32)
    rsa_cipher = PKCS1_OAEP.new(client_public_key)
    encrypted_aes_key = rsa_cipher.encrypt(aes_key)
    client_socket.send(encrypted_aes_key)
    print("AES key sent.")
    return aes_key

def encrypt_and_send_file(client_socket, aes_key):
    """Encrypts a file with AES-GCM and sends it to the client."""
    with open(FILE_TO_SEND, "rb") as f:
        plaintext = f.read()
    
    cipher_aes = AES.new(aes_key, AES.MODE_GCM)
    nonce = cipher_aes.nonce
    ciphertext, tag = cipher_aes.encrypt_and_digest(plaintext)
    
    client_socket.send(nonce)
    print("Nonce sent.")
    client_socket.send(tag)
    print("Tag sent.")
    client_socket.send(len(ciphertext).to_bytes(4, 'big'))
    client_socket.sendall(ciphertext)
    print("Encrypted file sent.")

"""Main entry point of the server."""
private_key = load_private_key("server_private.pem")
server_socket = setup_server()

while True:
    client_socket, client_address = server_socket.accept()
    print(f"Client connected: {client_address}")
    handle_client(client_socket, private_key)
