# Secure File Transfer System

## Overview
This project implements a secure file transfer system using cryptographic techniques to ensure confidentiality, integrity, and authenticity of the transferred data. The system uses RSA encryption for key exchange and AES-GCM for file encryption

## Requirements

### Python Version
- Python 3.10+ (Recommended version: Python 3.10 or higher).  
  You can download Python from [here](https://www.python.org/downloads/).

### Libraries
This project requires the following Python libraries:
- pycryptodome: Used for cryptographic algorithms (RSA, AES, ECDHE).
- unittest: Used for unit testing the file transfer functionality. (It comes pre-installed with Python).

To install the required libraries, run:
`pip install pycryptodome`


To check if you are using the correct version of Python, run:
`python --version`

Ensure that your Python version is 3.10 or higher.

## Project Structure


```
src/                  # Code to generate the keys
│
├── client/           # Client-side code and generated keys
├── server/           # Server-side code and generated keys
└── tests/            # Unit tests to verify file transfer functionality
```

## Usage
### 1. Generate RSA Key Pairs
Run the script to generate the RSA key pairs for both the server and client. The keys will be stored in their respective directories (src/server/ and src/client/).
```
cd src
python rsa_key_generator.py
```
This will generate:
```
server_private.pem, server_public.pem in src/server/
client_private.pem, client_public.pem in src/client/
```

### 2. Run the Server
Navigate to the server directory and run the server script:
```
cd src/server
python ft_server.py
```
The server will listen for incoming connections. The file file_to_transfer.txt is already created for testing. If you wish to use a different file, make sure to create it before running the server.

### 3. Run the Client
Navigate to the client directory and run the client script:
```
cd src/client
python ft_client.py
```
The client will connect to the server and begin the file transfer process. A new file, received_file.txt, will appear in the src/client/ directory. This file will be identical to the file_to_transfer.txt from the server.

### 4. Test the File Transfer
Run the unit tests to ensure the secure file transfer works as expected. This will automatically launch both the server and client scripts for testing.
```
cd src/tests
python tests_all.py
```

## Unit Tests Verify:

- Integrity and authenticity of transferred files.
- Proper encryption and decryption of files.
- Correct communication between server and client.
