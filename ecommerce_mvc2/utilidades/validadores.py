import re

def validar_email(email):
    """Validar formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validar_password(password):
    """Validar fortaleza de contraseña"""
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres"
    return True, ""

def validar_telefono(telefono):
    """Validar formato de teléfono"""
    pattern = r'^[0-9+\-\s()]{10,}$'
    return re.match(pattern, telefono) is not None

def validar_precio(precio):
    """Validar que el precio sea un número positivo"""
    try:
        precio_num = float(precio)
        return precio_num > 0
    except (ValueError, TypeError):
        return False