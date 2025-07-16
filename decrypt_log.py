from cryptography.fernet import Fernet

with open("encryption.key", "rb") as kf:
    key = kf.read()

fernet = Fernet(key)

with open("logs/keylog_2025-07-17_02-15-19.keylog", "rb") as ef:
    encrypted_data = ef.read()

decrypted = fernet.decrypt(encrypted_data).decode()
print(decrypted)
