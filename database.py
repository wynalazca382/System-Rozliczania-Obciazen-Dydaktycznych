from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base  # Użycie sqlalchemy.orm.declarative_base
import os
from dotenv import load_dotenv
load_dotenv()

engine = create_engine(os.getenv('DATABASE_URL'))
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