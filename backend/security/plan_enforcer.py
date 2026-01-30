from .api_key_auth import load_api_keys, save_api_keys

# Límites por plan (monthly)
PLAN_MONTHLY_LIMITS = {
    "free": 100,
    "pro": 10000,
    "enterprise": None  # Ilimitado
}

def get_monthly_limit(plan):
    """
    Obtiene el límite mensual para el plan.
    """
    return PLAN_MONTHLY_LIMITS.get(plan, 100)

def check_plan_limit(api_key, key_data):
    """
    Verifica si la API key ha excedido su límite mensual.
    Si sí, la bloquea automáticamente.
    Retorna (blocked, should_block)
    """
    if key_data.get('blocked', False):
        return True, False  # Ya bloqueada

    monthly_limit = key_data.get('monthly_limit')
    if monthly_limit is None:  # Enterprise ilimitado
        return False, False

    usage_count = key_data.get('usage_count', 0)
    if usage_count >= monthly_limit:
        # Bloquear automáticamente
        block_api_key(api_key)
        return True, True  # Bloqueada ahora

    return False, False

def block_api_key(api_key):
    """
    Bloquea la API key por exceder límite.
    """
    keys = load_api_keys()
    if api_key in keys:
        keys[api_key]['blocked'] = True
        save_api_keys(keys)

def unblock_api_key(api_key):
    """
    Desbloquea la API key (para admin o reset).
    """
    keys = load_api_keys()
    if api_key in keys:
        keys[api_key]['blocked'] = False
        save_api_keys(keys)