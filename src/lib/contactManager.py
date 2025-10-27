from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow


class ContactManager:
    SCOPES = ["https://www.googleapis.com/auth/contacts"]

    def __init__(
        self, credentials_file: str = "credentials.json", token_file: str = None
    ):
        """
        Inicializa ContactManager y configura la autenticación.
        Si existe token_file, lo usa para cargar credenciales ya autorizadas.
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.creds = None
        self.service = None
        self._autorizar()

    def _autorizar(self):

        base_dir = Path(__file__).resolve().parents[2]
        token_path = base_dir / "data" / "token.json"

        from os.path import exists

        if exists(token_path):
            # Cargar token.json existente
            self.creds = Credentials.from_authorized_user_file(
                str(token_path), self.SCOPES
            )
        else:
            # Flujo OAuth para primera autorización
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_file, self.SCOPES
            )
            self.creds = flow.run_local_server(port=8080)
            # Guardar token en data/token.json
            token_path.parent.mkdir(parents=True, exist_ok=True)
            with open(token_path, "w") as f:
                f.write(self.creds.to_json())

        self.service = build("people", "v1", credentials=self.creds)

    def crear_contacto(self, nombre: str, apellido1: str, apellido2: str, numero: str):
        """
        Crea un contacto en Google Contacts.
        """
        contact_body = {
            "names": [{"givenName": nombre, "familyName": f"{apellido1} {apellido2}"}],
            "phoneNumbers": [{"value": numero, "type": "mobile"}],
        }
        self.service.people().createContact(body=contact_body).execute()
        print(f"Contacto {nombre} {apellido1} {apellido2} creado correctamente.")

    def buscar_numeros(self, nombre: str, apellido1: str, apellido2: str):
        """
        Busca contactos que coincidan con el nombre y apellidos y devuelve sus números de teléfono.

        Args:
            nombre (str): Nombre del contacto.
            apellido1 (str): Primer apellido.
            apellido2 (str): Segundo apellido.

        Returns:
            List[str]: Lista de números de teléfono encontrados.
        """
        numeros = []
        query = f"{nombre} {apellido1} {apellido2}"

        results = (
            self.service.people()
            .searchContacts(query=query, readMask="names,phoneNumbers", pageSize=100)
            .execute()
        )

        for person in results.get("results", []):
            contact = person.get("person", {})
            phones = contact.get("phoneNumbers", [])
            for phone in phones:
                numeros.append(phone.get("value"))

        return numeros

    def borrar_por_numero(self, numero: str):
        """
        Borra todos los contactos que tengan el número de teléfono especificado.

        Args:
            numero (str): Número de teléfono a buscar.
        """
        # Buscar contactos por número
        results = (
            self.service.people()
            .searchContacts(query=numero, readMask="names,phoneNumbers", pageSize=100)
            .execute()
        )

        borrados = 0
        for person_entry in results.get("results", []):
            person = person_entry.get("person", {})
            phones = person.get("phoneNumbers", [])
            # Verificar si coincide exactamente el número
            if any(p.get("value") == numero for p in phones):
                resource_name = person.get("resourceName")
                if resource_name:
                    self.service.people().deleteContact(
                        resourceName=resource_name
                    ).execute()
                    borrados += 1

        print(f"Se borraron {borrados} contacto(s) con el número {numero}.")
