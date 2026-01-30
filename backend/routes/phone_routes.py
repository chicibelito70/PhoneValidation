from flask import Blueprint, request, jsonify
from services.phone_lookup_service import lookup_phone
from utils.validators import validate_international_phone
from security.api_key_auth import require_api_key

phone_bp = Blueprint('phone', __name__)

@phone_bp.route('/api/phone-lookup', methods=['GET'])
@require_api_key
def phone_lookup():
    """
    Endpoint para validar y enriquecer números telefónicos.
    Requiere API Key válida.
    Parámetro: phone (requerido, formato internacional)
    """
    phone = request.args.get('phone')

    if not phone:
        return jsonify({"error": "Parámetro 'phone' es requerido"}), 400

    if not validate_international_phone(phone):
        return jsonify({"error": "Formato de teléfono inválido. Use formato internacional (+1234567890)"}), 400

    try:
        result = lookup_phone(phone)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500