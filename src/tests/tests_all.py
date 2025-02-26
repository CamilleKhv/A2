import unittest
import subprocess
import os
import time

class TestSecureFileTransfer(unittest.TestCase):
    SERVER_SCRIPT = "../server/ft_server.py"
    CLIENT_SCRIPT = "../client/ft_client.py"
    TEST_FILE = "../server/file_to_transfer.txt"
    RECEIVED_FILE = "../client/received_file.txt"

    @classmethod
    def setUpClass(cls):
        """Prepare test files before running the tests."""
        print("\n🔹 Setting up test files...")
        
        cls.test_content = b"This is a secret shhhh."
        with open(cls.TEST_FILE, "wb") as f:
            f.write(cls.test_content)
        
        print(f"✅ Test file '{cls.TEST_FILE}' created with content: {cls.test_content}")

    @classmethod
    def tearDownClass(cls):
        """Clean up test files after tests."""
        print("\n🔹 Cleaning up test files...")
        
        if os.path.exists(cls.RECEIVED_FILE):
            os.remove(cls.RECEIVED_FILE)
            print(f"✅ Deleted received file: {cls.RECEIVED_FILE}")
        else:
            print("⚠️ No received file found to delete.")

    def test_file_transfer(self):
        """Test if the file is correctly encrypted and decrypted."""
        print("\n🚀 Starting secure file transfer test...")

        # Start the server in the background
        print("🔹 Launching server...")
        server_process = subprocess.Popen(
            ["python", self.SERVER_SCRIPT], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        
        # Wait a bit to ensure the server is running
        time.sleep(2)

        # Start the client to trigger file transfer
        print("🔹 Running client to start file transfer...")
        client_process = subprocess.run(
            ["python", self.CLIENT_SCRIPT], capture_output=True, text=True
        )

        # Print client output for debugging
        print("📜 Client Output:\n", client_process.stdout)
        if client_process.stderr:
            print("⚠️ Client Errors:\n", client_process.stderr)

        # Give some time for the transfer to complete
        time.sleep(2)

        # Stop the server
        print("🔹 Stopping the server...")
        server_process.terminate()
        server_process.wait()

        # Check if the received file exists
        print(f"🔹 Checking if received file '{self.RECEIVED_FILE}' exists...")
        self.assertTrue(os.path.exists(self.RECEIVED_FILE), "❌ Received file does not exist.")
        print("✅ Received file exists!")

        # Compare original and received file contents
        print("🔹 Comparing original and received file contents...")
        with open(self.RECEIVED_FILE, "rb") as f:
            received_content = f.read()

        if received_content == self.test_content:
            print("✅ File successfully transferred and decrypted!")
        else:
            print("❌ Decrypted file does not match original!")

        self.assertEqual(received_content, self.test_content, "❌ Decrypted file does not match original.")

if __name__ == '__main__':
    print("\n🧪 Running Secure File Transfer Tests...\n")
    unittest.main()
