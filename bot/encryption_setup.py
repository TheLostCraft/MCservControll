from cryptography.fernet import Fernet

with open("encrypt_key.txt", "w", encoding="utf-8") as datei:
    datei.write(Fernet.generate_key().decode())

print("Encrypt key setup complite")
