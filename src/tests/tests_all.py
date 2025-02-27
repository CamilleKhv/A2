import unittest
import os
import subprocess
import time

class TestSecureFileTransfer(unittest.TestCase):
    SERVER_SCRIPT = "../server/ft_server.py"
    CLIENT_SCRIPT = "../client/ft_client.py"
    SERVER_FILE = os.path.join(os.path.dirname(SERVER_SCRIPT), "file_to_transfer.txt")
    CLIENT_DIR = os.path.dirname(CLIENT_SCRIPT)
    RECEIVED_FILE = os.path.join(CLIENT_DIR, "received_file.txt")

    @classmethod
    def setUpClass(cls):
        print("Setting up test environment...")

        # Ensure the server file exists
        if not os.path.exists(cls.SERVER_FILE):
            raise FileNotFoundError(f"Server file not found: {cls.SERVER_FILE}")

        print(f"Using server file for testing: {cls.SERVER_FILE}")

    def test_file_transfer(self):
        print("Starting secure file transfer test...")

        # Start the server
        print("Launching server...")
        server_process = subprocess.Popen(["python", self.SERVER_SCRIPT], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(2)  # Give the server time to start

        # Start the client
        print("Running client to start file transfer...")
        client_process = subprocess.Popen(["python", self.CLIENT_SCRIPT], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        client_output, client_error = client_process.communicate()

        print("Client Output:\n", client_output.decode(errors="ignore"))  # Prevent decoding issues
        if client_error:
            print("Client Errors:\n", client_error.decode(errors="ignore"))

        # Stop the server
        print("Stopping the server...")
        server_process.terminate()
        server_process.wait()

        # Check if the received file exists **IN THE CLIENT DIRECTORY**
        print(f"Checking if received file exists: {self.RECEIVED_FILE}")
        self.assertTrue(os.path.exists(self.RECEIVED_FILE), "Received file does not exist.")

        # Compare file contents
        with open(self.SERVER_FILE, "rb") as f_sent, open(self.RECEIVED_FILE, "rb") as f_received:
            self.assertEqual(f_sent.read(), f_received.read(), "File contents do not match.")

    @classmethod
    def tearDownClass(cls):
        print("Cleaning up test files...")
        
        # Delete received file in client directory
        if os.path.exists(cls.RECEIVED_FILE):
            os.remove(cls.RECEIVED_FILE)
            print(f"Deleted received file: {cls.RECEIVED_FILE}")

if __name__ == "__main__":
    unittest.main()
