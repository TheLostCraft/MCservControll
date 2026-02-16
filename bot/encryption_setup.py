from cryptography.fernet import Fernet
import os

if os.path.exists("encrypt_key.txt"):
    print("The file 'encrypt_key.txt' already exists.")
else:
    with open("encrypt_key.txt", "w", encoding="utf-8") as datei:
        datei.write(Fernet.generate_key().decode())

    print("Encrypt key setup complite")
