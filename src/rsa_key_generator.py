from Crypto.PublicKey import RSA
import os

"""
A file to generate 2048-bit RSA key pairs for both the server and client.

Attributes : 
filename (str): the name of the key.
key (bytes): export the key in binary form.
is_private (bool): private or public key.

Method : 
generator_key(): creates the key to a file with appropriate permissions.
"""

def generator_key(filename, key, is_private=False):
    """
    Generates a file with a key in it and the permissions ensures that only the owner can read the private keys.
    
    Parameters :
    filename (str): the name of the key.
    key (bytes): export the key in binary form.
    is_private (bool): private or public key.
    """
    with open(filename, "wb") as file:
        file.write(key)
    if is_private:
        os.chmod(filename, 0o600)  # Restrict private key access

# Specify directories for the server and client
server_dir = os.path.join(os.getcwd(), "server")
client_dir = os.path.join(os.getcwd(), "client")

# Ensure the directories exist
os.makedirs(server_dir, exist_ok=True)
os.makedirs(client_dir, exist_ok=True)

# Generate Server Key Pair
server_key = RSA.generate(2048)
server_private_key = server_key.export_key()
server_public_key = server_key.publickey().export_key()

# Save the server keys in the server directory
server_private_key_path = os.path.join(server_dir, "server_private.pem")
server_public_key_path = os.path.join(server_dir, "server_public.pem")

generator_key(server_private_key_path, server_private_key, is_private=True)
generator_key(server_public_key_path, server_public_key)

print("Server keys generated and saved.")

# Generate Client Key Pair
client_key = RSA.generate(2048)
client_private_key = client_key.export_key()
client_public_key = client_key.publickey().export_key()

# Save the client keys in the client directory
client_private_key_path = os.path.join(client_dir, "client_private.pem")
client_public_key_path = os.path.join(client_dir, "client_public.pem")

generator_key(client_private_key_path, client_private_key, is_private=True)
generator_key(client_public_key_path, client_public_key)

print("Client keys generated and saved.")
