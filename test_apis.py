#!/usr/bin/env python3
"""
🧪 Script de Prueba para APIs - Phone Validation SaaS

Este script verifica que todas las APIs estén correctamente configuradas
y funcionando antes de iniciar el servidor principal.

Uso:
    python test_apis.py

Requiere:
    - Archivo .env configurado con todas las API keys
    - Conexión a internet
    - Python 3.8+
"""

import os
import sys
import asyncio
import httpx
from dotenv import load_dotenv
from typing import Dict, Any

# Cargar variables de entorno
load_dotenv()

class APITester:
    def __init__(self):
        self.numlookup_key = os.getenv('NUMLOOKUP_API_KEY')
        self.stripe_key = os.getenv('STRIPE_SECRET_KEY')
        self.results = {}

    async def test_numlookup_api(self) -> Dict[str, Any]:
        """Probar la API de NumLookup"""
        print("🔍 Probando NumLookup API...")

        if not self.numlookup_key:
            return {"status": "error", "message": "NUMLOOKUP_API_KEY no configurada"}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Probar con un número de ejemplo
                url = f"https://api.numlookupapi.com/v1/validate/+1234567890"
                params = {"apikey": self.numlookup_key}

                response = await client.get(url, params=params)
                response.raise_for_status()

                data = response.json()

                # Verificar respuesta básica
                if "valid" in data:
                    return {
                        "status": "success",
                        "message": "NumLookup API funcionando correctamente",
                        "sample_response": data
                    }
                else:
                    return {
                        "status": "warning",
                        "message": "Respuesta inesperada de NumLookup",
                        "response": data
                    }

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return {"status": "error", "message": "API Key de NumLookup inválida"}
            elif e.response.status_code == 429:
                return {"status": "error", "message": "Límite de rate alcanzado en NumLookup"}
            else:
                return {"status": "error", "message": f"Error HTTP {e.response.status_code}"}
        except Exception as e:
            return {"status": "error", "message": f"Error de conexión: {str(e)}"}

    async def test_stripe_api(self) -> Dict[str, Any]:
        """Probar la API de Stripe"""
        print("💳 Probando Stripe API...")

        if not self.stripe_key:
            return {"status": "error", "message": "STRIPE_SECRET_KEY no configurada"}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Crear un customer de prueba
                url = "https://api.stripe.com/v1/customers"
                headers = {
                    "Authorization": f"Bearer {self.stripe_key}",
                    "Content-Type": "application/x-www-form-urlencoded"
                }
                data = {"email": "test@example.com"}

                response = await client.post(url, headers=headers, data=data)
                response.raise_for_status()

                data = response.json()

                # Verificar que se creó el customer
                if data.get("id") and data.get("email") == "test@example.com":
                    # Limpiar: eliminar el customer de prueba
                    delete_url = f"https://api.stripe.com/v1/customers/{data['id']}"
                    await client.delete(delete_url, headers=headers)

                    return {
                        "status": "success",
                        "message": "Stripe API funcionando correctamente",
                        "customer_id": data["id"]
                    }
                else:
                    return {
                        "status": "warning",
                        "message": "Respuesta inesperada de Stripe",
                        "response": data
                    }

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return {"status": "error", "message": "API Key de Stripe inválida"}
            else:
                return {"status": "error", "message": f"Error HTTP {e.response.status_code}"}
        except Exception as e:
            return {"status": "error", "message": f"Error de conexión: {str(e)}"}

    def check_env_file(self) -> Dict[str, Any]:
        """Verificar que el archivo .env existe y tiene las variables necesarias"""
        print("📄 Verificando archivo .env...")

        required_vars = [
            'DATABASE_URL',
            'SECRET_KEY',
            'NUMLOOKUP_API_KEY',
            'STRIPE_SECRET_KEY'
        ]

        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        if missing_vars:
            return {
                "status": "error",
                "message": f"Variables faltantes en .env: {', '.join(missing_vars)}"
            }

        return {
            "status": "success",
            "message": "Archivo .env configurado correctamente"
        }

    async def run_all_tests(self):
        """Ejecutar todas las pruebas"""
        print("🚀 Iniciando pruebas de APIs...\n")

        # Verificar .env
        env_result = self.check_env_file()
        self.results['env'] = env_result
        print(f"📄 .env: {env_result['status'].upper()} - {env_result['message']}\n")

        if env_result['status'] == 'error':
            print("❌ Error crítico: Configura tu archivo .env antes de continuar")
            return

        # Probar APIs
        numlookup_result = await self.test_numlookup_api()
        self.results['numlookup'] = numlookup_result
        print(f"🔍 NumLookup: {numlookup_result['status'].upper()} - {numlookup_result['message']}")

        stripe_result = await self.test_stripe_api()
        self.results['stripe'] = stripe_result
        print(f"💳 Stripe: {stripe_result['status'].upper()} - {stripe_result['message']}\n")

        # Resumen
        self.print_summary()

    def print_summary(self):
        """Imprimir resumen de resultados"""
        print("📊 RESUMEN DE PRUEBAS")
        print("=" * 50)

        all_good = True
        for test_name, result in self.results.items():
            status_icon = "✅" if result['status'] == 'success' else "❌" if result['status'] == 'error' else "⚠️"
            print(f"{status_icon} {test_name.capitalize()}: {result['message']}")

            if result['status'] != 'success':
                all_good = False

        print("=" * 50)

        if all_good:
            print("🎉 ¡Todas las APIs están configuradas correctamente!")
            print("Puedes iniciar el servidor con: uvicorn app.main:app --reload")
        else:
            print("❌ Algunas APIs necesitan configuración. Revisa los errores arriba.")
            print("Consulta API_SETUP_GUIDE.md para más detalles.")

def main():
    """Función principal"""
    if sys.version_info < (3, 8):
        print("❌ Requiere Python 3.8 o superior")
        sys.exit(1)

    tester = APITester()
    asyncio.run(tester.run_all_tests())

if __name__ == "__main__":
    main()