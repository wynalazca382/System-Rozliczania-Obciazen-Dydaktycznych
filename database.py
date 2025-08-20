from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base  # Użycie sqlalchemy.orm.declarative_base
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from typing import Generator, Optional
load_dotenv()

key: Optional[str] = os.getenv("DB_KEY")
if key is None:
    raise ValueError("DB_KEY is not set in the environment variables")
f: Fernet = Fernet(key)

username: Optional[str] = os.getenv("DB_USER")
if username is None:
    raise ValueError("DB_USER is not set in the environment variables")

password_encrypted: Optional[str] = os.getenv("DB_PASSWORD")
if password_encrypted is None:
    raise ValueError("DB_PASSWORD is not set in the environment variables")

host: Optional[str] = os.getenv("DB_HOST")
if host is None:
    raise ValueError("DB_HOST is not set in the environment variables")

port: Optional[str] = os.getenv("DB_PORT")
if port is None:
    raise ValueError("DB_PORT is not set in the environment variables")

database: Optional[str] = os.getenv("DB_NAME")
if database is None:
    raise ValueError("DB_NAME is not set in the environment variables")

password: str = f.decrypt(password_encrypted.encode()).decode()
engine: Engine = create_engine(f"oracle+cx_oracle://{username}:{password}@{host}:{port}/{database}")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()  # Użycie nowej wersji declarative_base

def get_db() -> Generator[Session, None, None]:
    db: Session = SessionLocal()
    try:
        print("Nawiązano połączenie z bazą danych")
        yield db
    except Exception as e:
        print(f"Błąd podczas nawiązywania połączenia z bazą danych: {e}")
        raise
    finally:
        db.close()
