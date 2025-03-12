import unittest
import os
import subprocess
import time
import hashlib

class TestSecureFileTransfer(unittest.TestCase):
    """
    A test suite to ensure secure file transfer between server and client scripts.

    Attributes:
    SERVER_SCRIPT (str): Path to the server script.
    CLIENT_SCRIPT (str): Path to the client script.
    SERVER_FILE (str): Path to the file on the server to be transferred.
    CLIENT_DIR (str): Directory containing the client script.
    RECEIVED_FILE (str): Path to the received file in the tests directory.

    Methods:
    setUpClass(): Sets up the test environment, ensuring the server file exists.
    test_file_transfer(): Tests the secure file transfer process.
    test_key_exchange(): Validates that key exchange between client and server works.
    test_encryption_decryption(): Ensures encryption and decryption are correct.
    test_file_integrity(): Confirms that the received file has not been tampered with.
    """

    SERVER_SCRIPT = "../server/ft_server.py"  # Path to the server script
    CLIENT_SCRIPT = "../client/ft_client.py"  # Path to the client script
    SERVER_FILE = os.path.join(os.path.dirname(SERVER_SCRIPT), "file_to_transfer.txt")  # Path to file to send
    CLIENT_DIR = os.path.dirname(CLIENT_SCRIPT)  # Client directory
    RECEIVED_FILE = os.path.join(os.path.dirname(__file__), "received_file.txt")  # Path to the received file

    @classmethod
    def setUpClass(cls):
        """Sets up the test environment by ensuring the server file exists before tests are run."""
        print("Setting up test environment...")

        # Ensure the server file exists before starting tests
        if not os.path.exists(cls.SERVER_FILE):
            raise FileNotFoundError(f"Server file not found: {cls.SERVER_FILE}")

        print(f"Using server file for testing: {cls.SERVER_FILE}")

    def start_server(self):
        """Starts the server in a subprocess and waits for it to initialize."""
        print("Launching server...")
        server_process = subprocess.Popen(
            ["python", self.SERVER_SCRIPT], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        time.sleep(5)  # Allow extra time for the server to initialize and be ready
        return server_process

    def run_client(self):
        """Starts the client in a subprocess and returns its output."""
        print("Running client to start file transfer...")
        client_process = subprocess.Popen(
            ["python", self.CLIENT_SCRIPT], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        client_output, client_error = client_process.communicate()
        return client_output.decode(errors="ignore"), client_error.decode(errors="ignore") if client_error else ""

    def test_file_transfer(self):
        """Tests the secure file transfer from the server to the client."""
        print("Starting secure file transfer test...")

        server_process = self.start_server()
        client_output, client_error = self.run_client()

        # Print client output and any errors for debugging
        print("Client Output:\n", client_output)
        if client_error:
            print("Client Errors:\n", client_error)

        # Stop the server
        print("Stopping the server...")
        server_process.terminate()
        server_process.wait()

        # Ensure the received file exists
        self.assertTrue(os.path.exists(self.RECEIVED_FILE), "Received file does not exist.")

        # Compare file contents
        with open(self.SERVER_FILE, "rb") as f_sent, open(self.RECEIVED_FILE, "rb") as f_received:
            self.assertEqual(f_sent.read(), f_received.read(), "File contents do not match.")

    def test_key_exchange(self):
        """Ensures the client and server exchange AES keys correctly."""
        print("Starting key exchange validation test...")

        server_process = self.start_server()
        client_output, client_error = self.run_client()
        server_process.terminate()
        server_process.wait()

        # Check if the client receives the AES key (adjust based on your client-server implementation)
        self.assertIn("AES key received", client_output, "Client did not receive AES key.")
        self.assertIn("AES key decrypted", client_output, "AES key decryption failed.")

    def test_encryption_decryption(self):
        """Ensures that encrypted data is properly decrypted."""
        print("Starting encryption & decryption validation test...")

        server_process = self.start_server()
        client_output, client_error = self.run_client()
        server_process.terminate()
        server_process.wait()

        # Check if the encrypted file was received and decrypted
        self.assertTrue(os.path.exists(self.RECEIVED_FILE), "The received file does not exist")

        #Check if teh received file matches teh sended file after decryption
        with open(self.SERVER_FILE, "rb") as f_sent, open(self.RECEIVED_FILE, "rb") as f_received:
            self.assertEqual(f_sent.read(), f_received.read(), "The received file does not match after decryption")

    def test_file_integrity(self):
        """Validates that the received file matches the original using SHA-256 hashing."""
        print("Starting file integrity test...")

        server_process = self.start_server()
        client_output, client_error = self.run_client()
        server_process.terminate()
        server_process.wait()

        # Ensure the received file exists
        self.assertTrue(os.path.exists(self.RECEIVED_FILE), "Received file does not exist.")

        # Compute hash values for integrity check
        def get_file_hash(filename):
            hasher = hashlib.sha256()
            with open(filename, "rb") as f:
                while chunk := f.read(4096):
                    hasher.update(chunk)
            return hasher.hexdigest()

        original_hash = get_file_hash(self.SERVER_FILE)
        received_hash = get_file_hash(self.RECEIVED_FILE)

        print(f"Original file hash: {original_hash}")
        print(f"Received file hash: {received_hash}")

        # Ensure hashes match
        self.assertEqual(original_hash, received_hash, "File integrity check failed: Hashes do not match.")

if __name__ == "__main__":
    unittest.main()
