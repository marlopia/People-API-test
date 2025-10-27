import time
from lib.contactManager import ContactManager
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CREDENTIALS_FILE = BASE_DIR / "data" / "credentials.json"
TOKEN_FILE = BASE_DIR / "data" / "token.json"

manager = ContactManager(credentials_file=CREDENTIALS_FILE, token_file=TOKEN_FILE)
manager.crear_contacto("TEST", "APE1", "APE2", "+34600123123")

time.sleep(30)  # Ajustar sleep a latencia de refresco de la API

numeros = manager.buscar_numeros("TEST", "APE1", "APE2")

if len(numeros) == 0:
    print("No se han encontrado resultados")
else:
    for numero in numeros:
        print(numero)

manager.borrar_por_numero("+34600123123")

time.sleep(30)  # Ajustar sleep a latencia de refresco de la API

numeros = manager.buscar_numeros("TEST", "APE1", "APE2")

if len(numeros) == 0:
    print("No se han encontrado resultados")
else:
    for numero in numeros:
        print(numero)
