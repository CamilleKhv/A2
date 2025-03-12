import socket
import os
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP

"""
A file that implements secure key exchange and encrypted file transfer for the client.

Attributes:
SERVER_HOST (str): The server's host IP address.
SERVER_PORT (int): The server's listening port.
OUTPUT_FILE (str): The name of the file to save the decrypted content.
SUPPORTED_ENCRYPTIONS (list): List of supported encryption methods.

Methods:
- load_private_key(): Loads the client's private RSA key.
- load_public_key(): Loads the client's public RSA key.
- connect_to_server(): Establishes a connection with the server.
- perform_handshake(): Negotiates encryption method.
- exchange_keys(): Sends public key to server and receives AES key.
- receive_encrypted_file(): Receives and decrypts an encrypted file.
"""

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 65433
OUTPUT_FILE = "received_file.txt"  # The decrypted file will be saved as this
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Base directory of the script
SUPPORTED_ENCRYPTIONS = ["AES-GCM", "ChaCha20-Poly1305"]  # List of supported encryption methods

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

def perform_handshake(client_socket):
    """Negotiates encryption method with the server."""
    # Send the list of supported encryption methods (only one method in the list)
    client_socket.sendall(SUPPORTED_ENCRYPTIONS.encode())
    chosen_algo = client_socket.recv(1024).decode()
    print(f"Algo selected : {chosen_algo}")

def exchange_keys(client_socket, private_key):
    """Sends public key to the server and receives the AES key."""
    public_key = load_public_key("client_public.pem")
    client_socket.send(public_key)
    print("Public key sent to server.")
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
    file_size = int.from_bytes(client_socket.recv(4), 'big')
    encrypted_file_data = b""
    while len(encrypted_file_data) < file_size:
        chunk = client_socket.recv(min(4096, file_size - len(encrypted_file_data)))
        if not chunk:
            break
        encrypted_file_data += chunk
    print("Encrypted file received.")
    cipher_aes = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)
    plaintext = cipher_aes.decrypt_and_verify(encrypted_file_data, tag)
    with open(OUTPUT_FILE, "wb") as f:
        f.write(plaintext)
    print(f"Decrypted file saved as: {OUTPUT_FILE}")

private_key = load_private_key("client_private.pem")
client_socket = connect_to_server()
perform_handshake(client_socket)
aes_key = exchange_keys(client_socket, private_key)
receive_encrypted_file(client_socket, aes_key)
client_socket.close()
