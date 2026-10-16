"""Pruebas UNITARIAS de validadores y seguridad.
Técnicas: partición de equivalencia y análisis de valores límite."""
import pytest

from gestion_usuarios import validadores as v
from gestion_usuarios.seguridad import generar_hash, verificar_clave

pytestmark = pytest.mark.unitaria


# CP-01 / CP-02: correo
@pytest.mark.parametrize("correo", ["ana@umb.edu.co", "a.b+c@dominio.co", "  X@Y.COM  "])
def test_cp01_correo_valido(correo):
    assert v.validar_correo(correo) == []


@pytest.mark.parametrize("correo", ["", "sin-arroba.com", "a@b", "a@@b.com", "a b@c.com",
                                    "x" * 115 + "@a.com"])
def test_cp02_correo_invalido(correo):
    assert v.validar_correo(correo) != []


# CP-03 / CP-04: contraseña (valores límite 7, 8, 64, 65)
@pytest.mark.parametrize("clave", ["Abcdef1!", "Segura#2026", "Aa1!" + "x" * 60])
def test_cp03_clave_valida_y_limites(clave):
    assert v.validar_clave(clave) == []


@pytest.mark.parametrize("clave,fragmento", [
    ("Abcde1!", "entre 8 y 64"),                 # 7 caracteres
    ("Aa1!" + "x" * 61, "entre 8 y 64"),         # 65 caracteres
    ("segura#2026", "mayúscula"),
    ("SEGURA#2026", "minúscula"),
    ("Segura#Clave", "dígito"),
    ("Segura2026", "carácter especial"),
    ("", "entre 8 y 64"),
])
def test_cp04_clave_invalida(clave, fragmento):
    errores = v.validar_clave(clave)
    assert any(fragmento in e for e in errores)


# CP-05: nombre (límites 2, 3, 60, 61)
@pytest.mark.parametrize("nombre,valido", [
    ("Al", False), ("Ana", True), ("Ñ" * 60, True), ("A" * 61, False),
    ("José Pérez", True), ("Ana123", False), ("   ", False),
])
def test_cp05_nombre(nombre, valido):
    assert (v.validar_nombre(nombre) == []) is valido


# CP-06: rol
@pytest.mark.parametrize("rol,valido", [("estandar", True), ("administrador", True),
                                        ("root", False), ("", False)])
def test_cp06_rol(rol, valido):
    assert (v.validar_rol(rol) == []) is valido


# CP-07: hash de contraseña
def test_cp07_hash_no_guarda_texto_plano_y_verifica():
    h = generar_hash("Segura#2026")
    assert "Segura#2026" not in h
    assert verificar_clave("Segura#2026", h)
    assert not verificar_clave("Otra#2026x", h)


def test_cp07b_hash_usa_sal_aleatoria():
    assert generar_hash("Segura#2026") != generar_hash("Segura#2026")


def test_cp07c_hash_corrupto_no_lanza_excepcion():
    assert verificar_clave("x", "no-es-un-hash") is False
    assert verificar_clave("x", None) is False
