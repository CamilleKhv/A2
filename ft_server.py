import socket
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
import os

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 65433

"""
A file that  implements secure key exchange and encrypted file transfer.

Attributes : 

Methods : 
load_private_key(): 
setup_server():
handle_client():
exchange_keys():
encrypt_and_send_file():
"""

def load_private_key(filename):
    """Charge la clé privée RSA du serveur depuis un fichier."""
    with open(filename, "rb") as key_file:
        return RSA.import_key(key_file.read())
    
    # # Load server's private key
    # with open("server_private.pem", "rb") as key_file:
    #     private_key = RSA.import_key(key_file.read())

def setup_server():
    """Configure et démarre le serveur."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen()
    print(f"Server listening on {SERVER_HOST} {SERVER_PORT}...")
    return server_socket

#  # Set up the server
#     server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     server_socket.bind((SERVER_HOST, SERVER_PORT))
#     server_socket.listen()

#     print(f"Server listening on {SERVER_HOST} {SERVER_PORT}...")


def handle_client(client_socket, private_key):
    """Gère la communication avec un client."""
    client_public_key = RSA.import_key(client_socket.recv(2048))
    print("Client's public key received.")

    aes_key = exchange_keys(client_socket, client_public_key)
    encrypt_and_send_file(client_socket, aes_key)

    client_socket.close()

    # client_socket, client_address = server_socket.accept()
    # print(f"Client connected: {client_address}")

    #  # Receive the client's public RSA key
    # client_public_key = RSA.import_key(client_socket.recv(2048))
    # print("Client's public key received.")

def exchange_keys(client_socket, client_public_key):
    """Génère et envoie une clé AES chiffrée avec la clé publique du client."""
    aes_key = os.urandom(32)
    rsa_cipher = PKCS1_OAEP.new(client_public_key)
    encrypted_aes_key = rsa_cipher.encrypt(aes_key)
    
    client_socket.send(encrypted_aes_key)
    print("AES key sent.")
    
    return aes_key

    # # Generate AES key
    # aes_key = os.urandom(32)

    # # Encrypt AES key with client's public key
    # rsa_cipher = PKCS1_OAEP.new(client_public_key)
    # encrypted_aes_key = rsa_cipher.encrypt(aes_key)

    # # Send the encrypted AES key
    # client_socket.send(encrypted_aes_key)
    # print("AES key sent.")

def encrypt_and_send_file(client_socket, aes_key):
    """Chiffre un fichier avec AES-EAX et l'envoie au client."""
    cipher_aes = AES.new(aes_key, AES.MODE_EAX)
    nonce = cipher_aes.nonce
    plaintext = b"This is a test file for encryption."
    ciphertext, tag = cipher_aes.encrypt_and_digest(plaintext)

    client_socket.send(nonce)
    print("Nonce sent.")
    
    client_socket.send(ciphertext)
    print("Encrypted file sent.")

    #     # Encrypt a test file with AES-EAX
    # cipher_aes = AES.new(aes_key, AES.MODE_EAX)
    # nonce = cipher_aes.nonce  # Store the nonce
    # plaintext = b"This is a test file for encryption."
    # ciphertext, tag = cipher_aes.encrypt_and_digest(plaintext)

    # # Send nonce first
    # client_socket.send(nonce)
    # print("Nonce sent.")

    # # Send encrypted file
    # client_socket.send(ciphertext)
    # print("Encrypted file sent.")

    # client_socket.close()


"""Point d'entrée principal du serveur."""
private_key = load_private_key("server_private.pem")
server_socket = setup_server()

while True:  # Permet de gérer plusieurs connexions successives
    client_socket, client_address = server_socket.accept()
    print(f"Client connected: {client_address}")
    handle_client(client_socket, private_key)
