import socket
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 65433

def main():
    # Load private key
    with open("client_private.pem", "rb") as key_file:
        private_key = RSA.import_key(key_file.read())

    # Connect to server
    print("Connecting to the server...")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))

    print("Connected to server.")

    # Send public key to server
    with open("client_public.pem", "rb") as key_file:
        public_key = key_file.read()
    client_socket.send(public_key)
    print("Public key sent to server.")

    # Receive the encrypted AES key
    encrypted_aes_key = client_socket.recv(256)
    print(f"AES key received: {len(encrypted_aes_key)} bytes.")

    # Decrypt AES key with private key
    rsa_cipher = PKCS1_OAEP.new(private_key)
    aes_key = rsa_cipher.decrypt(encrypted_aes_key)
    print("AES key decrypted.")

    # Receive nonce from server
    nonce = client_socket.recv(16)  # AES nonce is 16 bytes
    print("Nonce received.")

    # Receive encrypted file
    encrypted_file_data = b""
    while True:
        chunk = client_socket.recv(4096)
        if not chunk:
            break
        encrypted_file_data += chunk
    print("Encrypted file received.")

    # Decrypt the file
    cipher_aes = AES.new(aes_key, AES.MODE_EAX, nonce=nonce)
    plaintext = cipher_aes.decrypt(encrypted_file_data)
    print(f"Decrypted message: {plaintext.decode()}")

    client_socket.close()

if __name__ == "__main__":
    main()
