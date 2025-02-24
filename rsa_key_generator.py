from Crypto.PublicKey import RSA

# Generate Server Key Pair
server_key = RSA.generate(2048)
server_private_key = server_key.export_key()
server_public_key = server_key.publickey().export_key()

with open("server_private.pem", "wb") as priv_file:
    priv_file.write(server_private_key)

with open("server_public.pem", "wb") as pub_file:
    pub_file.write(server_public_key)

print("Server keys generated and saved.")

# Generate Client Key Pair
client_key = RSA.generate(2048)
client_private_key = client_key.export_key()
client_public_key = client_key.publickey().export_key()

with open("client_private.pem", "wb") as priv_file:
    priv_file.write(client_private_key)

with open("client_public.pem", "wb") as pub_file:
    pub_file.write(client_public_key)

print("Client keys generated and saved.")
