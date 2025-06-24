import re

def extract_answer_data(user_answer: str):
    """
       Extrae datos de una cadena de texto usando patrones de regex mejorados.
       Maneja etiquetas combinadas como 'Teléfono/Correo' y datos separados por comas.
       """
    # Patrones regex mejorados:
    # 1. Incluimos 'Teléfono/Correo' como opción.
    # 2. Usamos ([^,\n]+) para capturar caracteres hasta la siguiente coma o un salto de línea.

    phone_pattern = re.compile(
        # La palabra clave puede ser 'Teléfono/Correo', 'Teléfono', etc.
        r'(Teléfono/Correo|Teléfono|Phone|Telefono)[:\s]*'
        # Captura todo lo que no sea una coma o un salto de línea
        r'([^,\n]+)',
        re.IGNORECASE
    )

    email_pattern = re.compile(
        r'(Correo electrónico|Correo|Email|E-mail)[:\s]*'
        r'([^,\n]+)',
        re.IGNORECASE
    )

    province_pattern = re.compile(
        r'(Provincia|Localización|Ubicación)[:\s]*'
        r'([^,\n]+)',
        re.IGNORECASE
    )

    # Extraer datos
    phone = phone_pattern.search(user_answer)
    email = email_pattern.search(user_answer)
    province = province_pattern.search(user_answer)

    # El operador ternario 'if phone else None' evita errores si no se encuentra coincidencia.
    data_extracted = {
        "phone": phone.group(2).strip() if phone else None,
        "email": email.group(2).strip() if email else None,
        "province": province.group(2).strip() if province else None,
    }

    # Consideración adicional: Si la etiqueta era 'Teléfono/Correo' y se extrajo un email,
    # el valor estaría en 'phone'. Podríamos añadir lógica para reclasificarlo.
    if data_extracted["phone"] and '@' in data_extracted["phone"]:
        # Es un email, movámoslo al campo correcto si el campo de email está vacío.
        if not data_extracted["email"]:
            data_extracted["email"] = data_extracted["phone"]
            data_extracted["phone"] = None

    return data_extracted


def validate_response_data(data_extracted):
    if not data_extracted["phone"] and not data_extracted["email"]:
        return False
    if not data_extracted["province"]:
        return False
    return True


def validate_answer_format_and_extract(user_answer: str):
    data = extract_answer_data(user_answer)
    is_valid = validate_response_data(data)
    return (is_valid, data)
