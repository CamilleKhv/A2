import unittest
import subprocess
import time
import os
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP

"""
A file that implements unit and system tests for secure key exchange and encrypted file transfer.

Attributes : 

Methods : 
test_rsa_key_generation(): Tests RSA key pair generation.
test_aes_key_encryption_decryption(): Tests AES key encryption and decryption.
test_aes_file_encryption_decryption(): Tests AES-GCM encryption and decryption.
test_end_to_end_file_transfer(): Tests the complete server-client interaction.
"""

class SecurityTests(unittest.TestCase):
    """Unit tests for encryption and key exchange."""

    def test_rsa_key_generation(self):
        """Test RSA key pair generation."""
        key = RSA.generate(2048)
        self.assertIsNotNone(key)
        self.assertIsNotNone(key.publickey())

    def test_aes_key_encryption_decryption(self):
        """Test AES key encryption and decryption with RSA."""
        key = RSA.generate(2048)
        rsa_cipher = PKCS1_OAEP.new(key.publickey())

        aes_key = os.urandom(32)
        encrypted_key = rsa_cipher.encrypt(aes_key)

        rsa_decipher = PKCS1_OAEP.new(key)
        decrypted_key = rsa_decipher.decrypt(encrypted_key)

        self.assertEqual(aes_key, decrypted_key)

    def test_aes_file_encryption_decryption(self):
        """Test AES-GCM encryption and decryption."""
        aes_key = os.urandom(32)
        cipher = AES.new(aes_key, AES.MODE_GCM)
        nonce = cipher.nonce
        plaintext = b"Test message"
        ciphertext, tag = cipher.encrypt_and_digest(plaintext)

        decipher = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)
        decrypted_text = decipher.decrypt_and_verify(ciphertext, tag)

        self.assertEqual(plaintext, decrypted_text)

class SystemTests(unittest.TestCase):
    """System test for full client-server interaction."""

    def test_end_to_end_file_transfer(self):
        """Test the full server-client file transfer process."""
        # Start the server in a separate process
        server_process = subprocess.Popen(["python", "ft_server.py"])
        
        # Give the server time to start
        time.sleep(2)

        # Run the client to test file transfer
        client_process = subprocess.run(["python", "ft_client.py"], capture_output=True, text=True)

        # Print client output for debugging
        print(client_process.stdout)

        # Check if decryption was successful (modify based on actual output)
        self.assertIn("Decrypted message:", client_process.stdout)

        # Stop the server after the test
        server_process.terminate()

"""Main entry point to run the tests."""
unittest.main()
