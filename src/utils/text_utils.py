import re


def format_name(full_name: str) -> str:
    txt = re.sub(r"\s+", " ", (full_name or "")).strip()

    if not txt:
        return ""

    if "," in txt:
        return txt

    parts = txt.split(" ")

    if len(parts) == 2:
        nombre = parts[0]
        apellido = parts[1]
        return f"{apellido}, {nombre}"

    if len(parts) == 4:
        nombres = " ".join(parts[:2])
        apellidos = " ".join(parts[2:])
        return f"{apellidos}, {nombres}"
    
    return txt