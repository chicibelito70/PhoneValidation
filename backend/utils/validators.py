import re

def validate_international_phone(phone):
    """
    Valida que el número telefónico tenga formato internacional básico.
    Debe empezar con + y contener solo dígitos después.
    """
    if not phone:
        return False
    # Patrón: + seguido de al menos 7 dígitos (mínimo internacional)
    pattern = r'^\+\d{7,15}$'
    return bool(re.match(pattern, phone))