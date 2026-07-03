from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os

load_dotenv(".env.prod")  # wczytuje DB_KEY z pliku
key = os.getenv("DB_KEY")
plain = "eW7ULYGQJ7a1"  # nowe hasło wprost
print(Fernet(key).encrypt(plain.encode()).decode())