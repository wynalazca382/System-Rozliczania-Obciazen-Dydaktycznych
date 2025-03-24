from sqlalchemy import create_engine, inspect, Column, String, Date, MetaData, text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.automap import automap_base
from dotenv import load_dotenv
import os

# Ładowanie konfiguracji bazy danych
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Tworzenie silnika bazy danych
engine = create_engine(DATABASE_URL)

metadata = MetaData()

# Pobierz listę synonimów i ich rzeczywiste nazwy
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT synonym_name, table_owner, table_name
        FROM all_synonyms
        WHERE owner = 'PENSUM_USR'
    """))
    synonym_mappings = {row[0]: (row[1], row[2]) for row in result}

# Pobieramy tabele/widoki do refleksji
for synonym, (schema, table_name) in synonym_mappings.items():
    print(f"🔹 Rejestruję: {synonym} -> {schema}.{table_name}")

    try:
        metadata.reflect(engine, schema=schema, views=True, only=[table_name])
    except Exception as e:
        print(f"⚠️ Nie można zarejestrować {synonym} ({schema}.{table_name}): {e}")

Base = automap_base(metadata=metadata)
Base.prepare()