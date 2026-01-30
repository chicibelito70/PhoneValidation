import json
import os
from functools import wraps
from flask import request, jsonify
from .rate_limiter import is_rate_limited, record_request
from .plan_enforcer import check_plan_limit

API_KEYS_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'api_keys.json')

def load_api_keys():
    """
    Carga las API keys desde el archivo JSON.
    """
    if os.path.exists(API_KEYS_FILE):
        with open(API_KEYS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_api_keys(keys):
    """
    Guarda las API keys en el archivo JSON.
    """
    with open(API_KEYS_FILE, 'w') as f:
        json.dump(keys, f, indent=2)

def validate_api_key(api_key):
    """
    Valida si la API key existe y está activa.
    """
    keys = load_api_keys()
    if api_key in keys and keys[api_key].get('active', False):
        return True, keys[api_key]
    return False, None

def increment_usage(api_key):
    """
    Incrementa el contador de uso para la API key.
    """
    keys = load_api_keys()
    if api_key in keys:
        keys[api_key]['usage_count'] = keys[api_key].get('usage_count', 0) + 1
        save_api_keys(keys)

def require_api_key(f):
    """
    Decorator para requerir API key válida, rate limit, plan enforcement y contar uso.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-KEY')
        if not api_key:
            return jsonify({"error": "API Key requerida"}), 401

        valid, key_data = validate_api_key(api_key)
        if not valid:
            return jsonify({"error": "API Key inválida o inactiva"}), 403

        # Verificar rate limit
        plan = key_data.get('plan', 'free')
        limited, retry_after = is_rate_limited(api_key, plan)
        if limited:
            return jsonify({
                "error": "Rate limit exceeded",
                "retry_after": retry_after
            }), 429

        # Verificar plan limit
        blocked, newly_blocked = check_plan_limit(api_key, key_data)
        if blocked:
            message = "Upgrade your plan to continue using the service"
            if newly_blocked:
                message = "Plan limit exceeded. " + message
            return jsonify({
                "error": "Plan limit exceeded",
                "message": message
            }), 403

        # Registrar el request
        record_request(api_key)

        # Incrementar contador de uso
        increment_usage(api_key)

        return f(*args, **kwargs)
    return decorated_function