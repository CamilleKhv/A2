import unittest
import os
import subprocess
import time

class TestSecureFileTransfer(unittest.TestCase):
    """
    A test suite to ensure secure file transfer between server and client scripts.

    Attributes:
    SERVER_SCRIPT (str): Path to the server script.
    CLIENT_SCRIPT (str): Path to the client script.
    SERVER_FILE (str): Path to the file on the server to be transferred.
    CLIENT_DIR (str): Directory containing the client script.
    RECEIVED_FILE (str): Path to the received file on the client side.

    Methods:
    setUpClass(): Sets up the test environment, ensuring the server file exists.
    test_file_transfer(): Tests the secure file transfer process.
    tearDownClass(): Cleans up test files after tests have run.
    """

    SERVER_SCRIPT = "../server/ft_server.py"
    CLIENT_SCRIPT = "../client/ft_client.py"
    SERVER_FILE = os.path.join(os.path.dirname(SERVER_SCRIPT), "file_to_transfer.txt")
    CLIENT_DIR = os.path.dirname(CLIENT_SCRIPT)
    RECEIVED_FILE = os.path.join(CLIENT_DIR, "received_file.txt")

    @classmethod
    def setUpClass(cls):
        """
        Sets up the test environment by ensuring the server file exists before tests are run.
        
        Raises:
        FileNotFoundError: If the server file does not exist.
        """
        print("Setting up test environment...")

        # Ensure the server file exists, as it's needed for the test
        if not os.path.exists(cls.SERVER_FILE):
            raise FileNotFoundError(f"Server file not found: {cls.SERVER_FILE}")

        print(f"Using server file for testing: {cls.SERVER_FILE}")

    def test_file_transfer(self):
        """
        Tests the secure file transfer from the server to the client.
        
        This method:
        - Starts the server process.
        - Starts the client process to initiate the file transfer.
        - Compares the content of the transferred file with the original.
        
        Raises:
        AssertionError: If the transferred file does not match the original file.
        """
        print("Starting secure file transfer test...")

        # Start the server in a subprocess
        print("Launching server...")
        server_process = subprocess.Popen(["python", self.SERVER_SCRIPT], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(2)  # Allow time for the server to start up

        # Start the client in a subprocess to begin file transfer
        print("Running client to start file transfer...")
        client_process = subprocess.Popen(["python", self.CLIENT_SCRIPT], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        client_output, client_error = client_process.communicate()

        # Print client output and any errors for debugging purposes
        print("Client Output:\n", client_output.decode(errors="ignore"))  # Ignore decoding issues
        if client_error:
            print("Client Errors:\n", client_error.decode(errors="ignore"))

        # Terminate the server after the client has completed the transfer
        print("Stopping the server...")
        server_process.terminate()
        server_process.wait()

        # Check if the received file exists in the client directory
        print(f"Checking if received file exists: {self.RECEIVED_FILE}")
        self.assertTrue(os.path.exists(self.RECEIVED_FILE), "Received file does not exist.")

        # Compare the contents of the original file on the server and the received file on the client
        with open(self.SERVER_FILE, "rb") as f_sent, open(self.RECEIVED_FILE, "rb") as f_received:
            self.assertEqual(f_sent.read(), f_received.read(), "File contents do not match.")

    @classmethod
    def tearDownClass(cls):
        """
        Cleans up the test environment by deleting the received file in the client directory.
        
        This method ensures that the received file is deleted after the test completes.
        """
        print("Cleaning up test files...")
        
        # Delete the received file in the client directory if it exists
        if os.path.exists(cls.RECEIVED_FILE):
            os.remove(cls.RECEIVED_FILE)
            print(f"Deleted received file: {cls.RECEIVED_FILE}")

if __name__ == "__main__":
    unittest.main()
