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

Methods:
- load_private_key(): Loads the client's private RSA key.
- load_public_key(): Loads the client's public RSA key.
- connect_to_server(): Establishes a connection with the server.
- exchange_keys(): Sends public key to server and receives AES key.
- receive_encrypted_file(): Receives and decrypts an encrypted file.
"""

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 65433
OUTPUT_FILE = "received_file.txt"  # The decrypted file will be saved as this
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Base directory of the script


def load_private_key(filename):
    """Loads the client's private RSA key from a file."""
    key_path = os.path.join(BASE_DIR, filename)  # Get the path to the private key file
    with open(key_path, "rb") as key_file:
        return RSA.import_key(key_file.read())  # Import and return the RSA private key

def load_public_key(filename):
    """Loads the client's public RSA key from a file."""
    key_path = os.path.join(BASE_DIR, filename)  # Get the path to the public key file
    with open(key_path, "rb") as key_file:
        return key_file.read()  # Return the public key as bytes

def connect_to_server():
    """Establishes a connection with the server."""
    print("Connecting to the server...")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a TCP/IP socket
    client_socket.connect((SERVER_HOST, SERVER_PORT))  # Connect to the server
    print("Connected to server.")
    return client_socket  # Return the socket object

def exchange_keys(client_socket, private_key):
    """Sends public key to the server and receives the AES key."""
    public_key = load_public_key("client_public.pem")  # Load the client's public key
    client_socket.send(public_key)  # Send public key to the server
    print("Public key sent to server.")

    # Receive and decrypt AES key
    encrypted_aes_key = client_socket.recv(256)  # Receive the encrypted AES key
    print(f"AES key received: {len(encrypted_aes_key)} bytes.")

    rsa_cipher = PKCS1_OAEP.new(private_key)  # Initialize the RSA cipher with the private key
    aes_key = rsa_cipher.decrypt(encrypted_aes_key)  # Decrypt the AES key using the RSA cipher
    print("AES key decrypted.")

    return aes_key  # Return the decrypted AES key

def receive_encrypted_file(client_socket, aes_key):
    """Receives and decrypts an encrypted file from the server."""
    nonce = client_socket.recv(16)  # Receive the nonce used for AES-GCM encryption
    print("Nonce received.")

    tag = client_socket.recv(16)  # Receive the authentication tag for AES-GCM
    print("Tag received.")

    # Receive file size first
    file_size = int.from_bytes(client_socket.recv(4), 'big')  # Receive the size of the file as a 4-byte integer

    encrypted_file_data = b""  # Initialize an empty byte string to hold the encrypted file data
    while len(encrypted_file_data) < file_size:
        chunk = client_socket.recv(min(4096, file_size - len(encrypted_file_data)))  # Receive file data in chunks
        if not chunk:
            break
        encrypted_file_data += chunk  # Add the received chunk to the encrypted data
    print("Encrypted file received.")

    # Decrypt using AES-GCM
    cipher_aes = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)  # Initialize AES cipher in GCM mode with nonce
    plaintext = cipher_aes.decrypt_and_verify(encrypted_file_data, tag)  # Decrypt and verify the file data using the tag

    # Save decrypted content to a file
    with open(OUTPUT_FILE, "wb") as f:
        f.write(plaintext)  # Write the decrypted content to the output file
    print(f"Decrypted file saved as: {OUTPUT_FILE}")

"""Main entry point of the client."""
private_key = load_private_key("client_private.pem")  # Load the client's private key
client_socket = connect_to_server()  # Establish a connection to the server

aes_key = exchange_keys(client_socket, private_key)  # Exchange keys with the server
receive_encrypted_file(client_socket, aes_key)  # Receive and decrypt the encrypted file

client_socket.close()  # Close the connection to the server
