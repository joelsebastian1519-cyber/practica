"""Funciones de seguridad: hash de contraseñas y bloqueo por intentos."""
import hashlib
import hmac
import secrets

ITERACIONES = 120_000
MAX_INTENTOS_FALLIDOS = 3


def generar_hash(clave: str, sal: bytes | None = None) -> str:
    """Devuelve 'sal_hex$hash_hex' usando PBKDF2-HMAC-SHA256."""
    sal = sal if sal is not None else secrets.token_bytes(16)
    derivada = hashlib.pbkdf2_hmac("sha256", clave.encode("utf-8"), sal, ITERACIONES)
    return f"{sal.hex()}${derivada.hex()}"


def verificar_clave(clave: str, hash_guardado: str) -> bool:
    try:
        sal_hex, _ = hash_guardado.split("$", 1)
        sal = bytes.fromhex(sal_hex)
    except (ValueError, AttributeError):
        return False
    return hmac.compare_digest(generar_hash(clave, sal), hash_guardado)
