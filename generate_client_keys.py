from Crypto.PublicKey import RSA

# Generate key pair for client
key = RSA.generate(2048)
private_key = key.export_key()
public_key = key.publickey().export_key()

# Save keys to files
with open("client_private.pem", "wb") as priv_file:
    priv_file.write(private_key)

with open("client_public.pem", "wb") as pub_file:
    pub_file.write(public_key)

print("Client keys generated and saved.")
