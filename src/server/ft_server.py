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
FILE_TO_SEND = "file_to_transfer.txt"  # File that will be encrypted and sent


def load_private_key(filename):
    """Loads the server's private RSA key from a file."""
    with open(filename, "rb") as key_file:
        return RSA.import_key(key_file.read())  # Read and import the server's private key

def setup_server():
    """Configures and starts the server."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a TCP/IP socket
    server_socket.bind((SERVER_HOST, SERVER_PORT))  # Bind the socket to the server host and port
    server_socket.listen()  # Start listening for incoming connections
    print(f"Server listening on {SERVER_HOST} {SERVER_PORT}...")
    return server_socket  # Return the server socket object

def handle_client(client_socket, private_key):
    """Handles communication with a client."""
    
    # Receive the client's public key
    client_public_key = RSA.import_key(client_socket.recv(2048))  # Receive the client's public key
    print("Client's public key received.")

    # Generate and send AES key
    aes_key = exchange_keys(client_socket, client_public_key)  # Generate and send AES key encrypted with client's public key

    # Encrypt and send a file securely
    encrypt_and_send_file(client_socket, aes_key)  # Encrypt the file using AES and send to the client

    client_socket.close()  # Close the connection to the client

def exchange_keys(client_socket, client_public_key):
    """Generates and sends an AES key encrypted with the client's public key."""
    
    # Generate a random 256-bit AES key
    aes_key = os.urandom(32)  # Generate a random 256-bit key for AES encryption

    # Encrypt the AES key using the client's public RSA key
    rsa_cipher = PKCS1_OAEP.new(client_public_key)  # Initialize RSA cipher for encryption
    encrypted_aes_key = rsa_cipher.encrypt(aes_key)  # Encrypt the AES key

    # Send the encrypted AES key to the client
    client_socket.send(encrypted_aes_key)  
    print("AES key sent.")
    
    return aes_key  # Return the generated AES key for further encryption

def encrypt_and_send_file(client_socket, aes_key):
    """Encrypts a file with AES-GCM and sends it to the client."""

    # Read the file in binary mode
    with open(FILE_TO_SEND, "rb") as f:
        plaintext = f.read()  # Read the file content into plaintext

    # Create AES-GCM cipher for encryption
    cipher_aes = AES.new(aes_key, AES.MODE_GCM)  # Initialize AES cipher in GCM mode
    nonce = cipher_aes.nonce  # AES-GCM requires a nonce for encryption
    
    # Encrypt the file and get the authentication tag for integrity verification
    ciphertext, tag = cipher_aes.encrypt_and_digest(plaintext)

    # Send nonce first, which is needed for decryption
    client_socket.send(nonce)
    print("Nonce sent.")

    # Send the authentication tag for AES-GCM
    client_socket.send(tag)  # AES-GCM requires sending the tag separately for verification
    print("Tag sent.")

    # Send the encrypted file size first (to handle large files properly)
    client_socket.send(len(ciphertext).to_bytes(4, 'big'))  # Send the file size as 4-byte integer

    # Send the encrypted file content
    client_socket.sendall(ciphertext)  # Send the encrypted file data to the client
    print("Encrypted file sent.")

"""Main entry point of the server."""
private_key = load_private_key("server_private.pem")  # Load the server's private key
server_socket = setup_server()  # Setup the server

while True:  # Allows handling multiple connections
    client_socket, client_address = server_socket.accept()  # Accept incoming client connections
    print(f"Client connected: {client_address}")
    handle_client(client_socket, private_key)  # Handle communication with the connected client
