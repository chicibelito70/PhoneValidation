from flask import Blueprint, jsonify
from security.api_key_auth import load_api_keys

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/api/admin/usage', methods=['GET'])
def get_usage():
    """
    Endpoint para obtener el uso de las API keys.
    Devuelve owner y usage_count, con keys enmascaradas.
    """
    keys = load_api_keys()
    usage_data = []
    for api_key, data in keys.items():
        masked_key = api_key[:10] + '***'  # Enmascarar la key
        usage_data.append({
            "api_key": masked_key,
            "owner": data.get("owner", "unknown"),
            "usage_count": data.get("usage_count", 0)
        })
    return jsonify(usage_data)