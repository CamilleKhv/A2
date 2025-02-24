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

# Generate Server Key Pair
server_key = RSA.generate(2048)
server_private_key = server_key.export_key()
server_public_key = server_key.publickey().export_key()

generator_key("server_private.pem", server_private_key, is_private=True)
generator_key("server_public.pem", server_public_key)

print("Server keys generated and saved.")

# Generate Client Key Pair
client_key = RSA.generate(2048)
client_private_key = client_key.export_key()
client_public_key = client_key.publickey().export_key()

generator_key("client_private.pem", client_private_key, is_private=True)
generator_key("client_public.pem", client_public_key)

print("Client keys generated and saved.")
