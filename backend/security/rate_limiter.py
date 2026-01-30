import time
from flask import jsonify

# Almacenamiento en memoria para rate limits
rate_limits = {}

# Límites por plan (requests por minuto)
PLAN_LIMITS = {
    "free": 10,
    "pro": 100,
    "enterprise": 1000
}

WINDOW_SIZE = 60  # 1 minuto

def get_plan_limit(plan):
    """
    Obtiene el límite para el plan dado.
    """
    return PLAN_LIMITS.get(plan, 10)  # Default a free si no existe

def is_rate_limited(api_key, plan):
    """
    Verifica si la API key ha excedido el rate limit.
    """
    current_time = time.time()
    window_start = current_time - WINDOW_SIZE

    if api_key not in rate_limits:
        rate_limits[api_key] = []

    # Limpiar requests antiguas
    rate_limits[api_key] = [t for t in rate_limits[api_key] if t > window_start]

    limit = get_plan_limit(plan)
    if len(rate_limits[api_key]) >= limit:
        # Calcular tiempo hasta reset
        if rate_limits[api_key]:
            retry_after = int(WINDOW_SIZE - (current_time - rate_limits[api_key][0]))
        else:
            retry_after = WINDOW_SIZE
        return True, retry_after

    return False, 0

def record_request(api_key):
    """
    Registra un request para la API key.
    """
    current_time = time.time()
    if api_key not in rate_limits:
        rate_limits[api_key] = []
    rate_limits[api_key].append(current_time)