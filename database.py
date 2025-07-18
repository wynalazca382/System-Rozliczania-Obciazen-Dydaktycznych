from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base  # Użycie sqlalchemy.orm.declarative_base
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet
load_dotenv()

key = b'oHsfpCOmkXSW_8kurz8Couwvv1xhO0bg3ax2w0gB1WQ='
f = Fernet(key)
username = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
database = os.getenv("DB_NAME")
password = f.decrypt(password.encode()).decode()
engine = create_engine(f"oracle+cx_oracle://{username}:{password}@{host}:{port}/{database}")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()  # Użycie nowej wersji declarative_base

def get_db():
    try:
        db = SessionLocal()
        print("Nawiązano połączenie z bazą danych")
        yield db
    except Exception as e:
        print(f"Błąd podczas nawiązywania połączenia z bazą danych: {e}")
        raise
    finally:
        db.close()