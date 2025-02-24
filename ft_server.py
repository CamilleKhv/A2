import socket
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import os

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 65433  # Make sure this matches with the client

def main():
    # Load server's private key
    with open("server_private.pem", "rb") as key_file:
        private_key = RSA.import_key(key_file.read())

    # Set up the server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen()

    print(f"Server listening on {SERVER_HOST} {SERVER_PORT}...")

    # Accept client connection
    client_socket, client_address = server_socket.accept()
    print(f"Client connected: {client_address}")

    # Receive the client's public RSA key
    client_public_key_data = client_socket.recv(2048)
    client_public_key = RSA.import_key(client_public_key_data)
    print("Client's public key received.")

    # Generate a random AES key (32 bytes for AES-256)
    aes_key = os.urandom(32)

    # Encrypt AES key using client's public key
    cipher_rsa = PKCS1_OAEP.new(client_public_key)
    encrypted_aes_key = cipher_rsa.encrypt(aes_key)

    # Send the encrypted AES key to the client
    client_socket.send(encrypted_aes_key)
    print("Encrypted AES key sent to the client.")

    # Receive acknowledgment from the client
    ack_message = client_socket.recv(1024)
    print(f"Acknowledgment from client: {ack_message.decode()}")

    # Send a test message to the client
    client_socket.send(b"Hello from server!")
    print("Test message sent to client.")

    client_socket.close()

if __name__ == "__main__":
    main()
