import os
import sys
from dotenv import load_dotenv
from typing import NoReturn

def load_app_config() -> None:
    """
    Wczytuje konfigurację na podstawie argumentu wiersza poleceń --env.
    Domyślnie używa 'prod', jeśli nie podano argumentu.
    """
    env: str = 'prod'
    if '--env' in sys.argv:
        try:
            # Pobierz wartość po fladze --env
            env = sys.argv[sys.argv.index('--env') + 1]
        except IndexError:
            print("Ostrzeżenie: Użyto flagi --env, ale nie podano środowiska. Używam 'prod'.")
    
    if env not in ['prod', 'test']:
        print(f"Ostrzeżenie: Nieprawidłowe środowisko '{env}'. Używam 'prod'.")
        env = 'prod'

    config_path: str = f".env.{env}"
    
    if os.path.exists(config_path):
        load_dotenv(dotenv_path=config_path, override=True)
        print(f"Pomyślnie wczytano konfigurację dla środowiska '{env}' z pliku '{config_path}'")
    else:
        raise FileNotFoundError(f"Plik konfiguracyjny '{config_path}' nie został znaleziony. Aplikacja nie może zostać uruchomiona.") 
