import socket
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
import os

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 65433

def main():
    # Load server's private key
    with open("server_private.pem", "rb") as key_file:
        private_key = RSA.import_key(key_file.read())

    # Set up the server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen()

    print(f"Server listening on {SERVER_HOST} {SERVER_PORT}...")

    client_socket, client_address = server_socket.accept()
    print(f"Client connected: {client_address}")

    # Receive the client's public RSA key
    client_public_key = RSA.import_key(client_socket.recv(2048))
    print("Client's public key received.")

    # Generate AES key
    aes_key = os.urandom(32)

    # Encrypt AES key with client's public key
    rsa_cipher = PKCS1_OAEP.new(client_public_key)
    encrypted_aes_key = rsa_cipher.encrypt(aes_key)

    # Send the encrypted AES key
    client_socket.send(encrypted_aes_key)
    print("AES key sent.")

    # Encrypt a test file with AES-EAX
    cipher_aes = AES.new(aes_key, AES.MODE_EAX)
    nonce = cipher_aes.nonce  # Store the nonce
    plaintext = b"This is a test file for encryption."
    ciphertext, tag = cipher_aes.encrypt_and_digest(plaintext)

    # Send nonce first
    client_socket.send(nonce)
    print("Nonce sent.")

    # Send encrypted file
    client_socket.send(ciphertext)
    print("Encrypted file sent.")

    client_socket.close()

if __name__ == "__main__":
    main()
