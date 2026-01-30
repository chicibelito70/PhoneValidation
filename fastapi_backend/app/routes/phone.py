from fastapi import APIRouter, Depends, HTTPException
from ..middlewares import api_key_middleware

router = APIRouter()

@router.get("/lookup")
async def phone_lookup(phone: str):
    # Aquí iría la lógica de validación de teléfono
    # Usando el middleware para validar API key y rate limit
    return {"valid": True, "phone": phone, "country": "US", "carrier": "Verizon", "line_type": "mobile"}