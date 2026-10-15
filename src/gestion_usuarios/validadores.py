"""Reglas de validación de datos de entrada del módulo de usuarios.

Cada función devuelve una lista de mensajes de error; una lista vacía
significa que el dato es válido. Esto facilita las pruebas unitarias y
permite mostrar todos los errores al usuario a la vez.
"""
import re

ROLES_VALIDOS = ("estandar", "administrador")

_PATRON_CORREO = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
_PATRON_NOMBRE = re.compile(r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü ]+$")

LONGITUD_MIN_CLAVE = 8
LONGITUD_MAX_CLAVE = 64
LONGITUD_MIN_NOMBRE = 3
LONGITUD_MAX_NOMBRE = 60


def normalizar_correo(correo: str) -> str:
    """Quita espacios y pasa a minúsculas (corrección del defecto DEF-001)."""
    return (correo or "").strip().lower()


def validar_correo(correo: str) -> list[str]:
    correo = normalizar_correo(correo)
    if not correo:
        return ["El correo es obligatorio."]
    if len(correo) > 120:
        return ["El correo no puede superar 120 caracteres."]
    if not _PATRON_CORREO.match(correo):
        return ["El correo no tiene un formato válido."]
    return []


def validar_nombre(nombre: str) -> list[str]:
    nombre = (nombre or "").strip()
    if not nombre:
        return ["El nombre es obligatorio."]
    errores = []
    if not LONGITUD_MIN_NOMBRE <= len(nombre) <= LONGITUD_MAX_NOMBRE:
        errores.append(
            f"El nombre debe tener entre {LONGITUD_MIN_NOMBRE} y "
            f"{LONGITUD_MAX_NOMBRE} caracteres."
        )
    if not _PATRON_NOMBRE.match(nombre):
        errores.append("El nombre solo puede contener letras y espacios.")
    return errores


def validar_clave(clave: str) -> list[str]:
    """Política de contraseñas: 8-64 caracteres, mayúscula, minúscula,
    dígito y carácter especial."""
    clave = clave or ""
    errores = []
    if not LONGITUD_MIN_CLAVE <= len(clave) <= LONGITUD_MAX_CLAVE:
        errores.append(
            f"La contraseña debe tener entre {LONGITUD_MIN_CLAVE} y "
            f"{LONGITUD_MAX_CLAVE} caracteres."
        )
    if not re.search(r"[A-Z]", clave):
        errores.append("La contraseña debe incluir una letra mayúscula.")
    if not re.search(r"[a-z]", clave):
        errores.append("La contraseña debe incluir una letra minúscula.")
    if not re.search(r"\d", clave):
        errores.append("La contraseña debe incluir un dígito.")
    if not re.search(r"[^A-Za-z0-9]", clave):
        errores.append("La contraseña debe incluir un carácter especial.")
    return errores


def validar_rol(rol: str) -> list[str]:
    if rol not in ROLES_VALIDOS:
        return [f"Rol inválido. Valores permitidos: {', '.join(ROLES_VALIDOS)}."]
    return []
