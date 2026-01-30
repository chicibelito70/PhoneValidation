import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('NUMLOOKUP_API_KEY')
BASE_URL = 'https://api.numlookupapi.com/v1/validate'

def lookup_phone(phone):
    """
    Consulta la API externa para validar y enriquecer el número telefónico.
    Retorna un diccionario con los datos normalizados o lanza excepción.
    """
    if not API_KEY:
        raise ValueError("API Key no configurada")

    url = f"{BASE_URL}/{phone}?apikey={API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Normalizar respuesta
        return {
            "valid": data.get("valid", False),
            "phone": phone,
            "country": data.get("country_name", ""),
            "carrier": data.get("carrier", ""),
            "line_type": data.get("line_type", "")
        }
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error al consultar API externa: {str(e)}")