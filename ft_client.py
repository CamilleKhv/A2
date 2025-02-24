import socket
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 65433  # Make sure this matches with the server

def main():
    # Load client's private key
    with open("client_private.pem", "rb") as key_file:
        private_key = RSA.import_key(key_file.read())

    # Load client's public key
    with open("client_public.pem", "rb") as key_file:
        client_public_key = RSA.import_key(key_file.read())

    # Connect to server
    print("Connecting to the server...")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))
    print("Connected to server.")

    # Send client's public RSA key to the server
    client_socket.send(client_public_key.export_key())
    print("Client's public key sent to server.")

    # Receive the encrypted AES key from the server
    encrypted_aes_key = client_socket.recv(256)  # RSA-encrypted AES key
    print(f"Encrypted AES key received: {len(encrypted_aes_key)} bytes.")

    # Decrypt AES key using client's private key
    cipher_rsa = PKCS1_OAEP.new(private_key)
    aes_key = cipher_rsa.decrypt(encrypted_aes_key)
    print("AES key decrypted successfully.")

    # Send acknowledgment to the server
    client_socket.send(b"AES key received and decrypted")
    print("Acknowledgment sent to server.")

    # Receive test message from the server
    test_message = client_socket.recv(1024)
    print(f"Received from server: {test_message.decode()}")

    client_socket.close()

if __name__ == "__main__":
    main()
