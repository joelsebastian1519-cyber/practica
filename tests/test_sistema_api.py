"""Pruebas de SISTEMA / funcionales de extremo a extremo sobre la API REST."""
import pytest

from conftest import CLAVE_OK, login

pytestmark = pytest.mark.sistema


def test_cp26_flujo_completo_registro_login_edicion_eliminacion(app_cliente):
    c = app_cliente
    r = c.post("/usuarios", json={"nombre": "Sara Ruiz", "correo": "sara@umb.edu.co",
                                  "clave": CLAVE_OK})
    assert r.status_code == 201
    uid = r.get_json()["id"]
    h = login(c, "sara@umb.edu.co")
    assert c.get(f"/usuarios/{uid}", headers=h).get_json()["nombre"] == "Sara Ruiz"
    r = c.put(f"/usuarios/{uid}", json={"nombre": "Sara Ruiz Díaz"}, headers=h)
    assert r.status_code == 200 and r.get_json()["nombre"] == "Sara Ruiz Díaz"
    assert c.delete(f"/usuarios/{uid}", headers=h).status_code == 204
    assert c.get(f"/usuarios/{uid}", headers=h).status_code == 401   # sesión invalidada


def test_cp27_registro_invalido_devuelve_400_con_detalles(app_cliente):
    r = app_cliente.post("/usuarios", json={"nombre": "", "correo": "x", "clave": "1"})
    assert r.status_code == 400 and len(r.get_json()["detalles"]) >= 3


def test_cp27b_cuerpo_vacio_o_no_json(app_cliente):
    assert app_cliente.post("/usuarios", data="texto").status_code == 400


def test_cp28_registro_duplicado_devuelve_409(app_cliente):
    datos = {"nombre": "Sara Ruiz", "correo": "sara@umb.edu.co", "clave": CLAVE_OK}
    app_cliente.post("/usuarios", json=datos)
    assert app_cliente.post("/usuarios", json=datos).status_code == 409


@pytest.mark.seguridad
def test_cp29_respuesta_nunca_expone_hash(app_cliente):
    r = app_cliente.post("/usuarios", json={"nombre": "Sara Ruiz", "correo": "s@umb.edu.co",
                                            "clave": CLAVE_OK})
    cuerpo = r.get_data(as_text=True)
    assert "hash" not in cuerpo and CLAVE_OK not in cuerpo


@pytest.mark.seguridad
def test_cp30_registro_anonimo_no_puede_autoasignarse_admin(app_cliente):
    r = app_cliente.post("/usuarios", json={"nombre": "Pirata", "correo": "p@umb.edu.co",
                                            "clave": CLAVE_OK, "rol": "administrador"})
    assert r.get_json()["rol"] == "estandar"


@pytest.mark.seguridad
@pytest.mark.parametrize("cabecera", [None, "Bearer token-falso", "Basic abc"])
def test_cp31_endpoints_protegidos_sin_token_valido(app_cliente, cabecera):
    h = {"Authorization": cabecera} if cabecera else {}
    assert app_cliente.get("/usuarios", headers=h).status_code == 401


def test_cp32_login_incorrecto_devuelve_401(app_cliente):
    r = app_cliente.post("/login", json={"correo": "admin@umb.edu.co", "clave": "Mala#2026x"})
    assert r.status_code == 401


def test_cp33_admin_lista_y_cambia_rol(app_cliente):
    c = app_cliente
    uid = c.post("/usuarios", json={"nombre": "Sara Ruiz", "correo": "sara@umb.edu.co",
                                    "clave": CLAVE_OK}).get_json()["id"]
    h_admin = login(c, "admin@umb.edu.co")
    assert len(c.get("/usuarios", headers=h_admin).get_json()) == 2
    r = c.put(f"/usuarios/{uid}/rol", json={"rol": "administrador"}, headers=h_admin)
    assert r.get_json()["rol"] == "administrador"


@pytest.mark.seguridad
def test_cp34_estandar_recibe_403_en_rutas_de_admin(app_cliente):
    c = app_cliente
    c.post("/usuarios", json={"nombre": "Sara Ruiz", "correo": "sara@umb.edu.co",
                              "clave": CLAVE_OK})
    h = login(c, "sara@umb.edu.co")
    assert c.get("/usuarios", headers=h).status_code == 403
    assert c.get("/usuarios/1", headers=h).status_code == 403
    assert c.put("/usuarios/1/rol", json={"rol": "estandar"}, headers=h).status_code == 403


def test_cp35_usuario_inexistente_devuelve_404(app_cliente):
    h = login(app_cliente, "admin@umb.edu.co")
    assert app_cliente.get("/usuarios/999", headers=h).status_code == 404


def test_cp36_sesion_de_usuario_eliminado_por_admin_queda_invalida(app_cliente):
    c = app_cliente
    uid = c.post("/usuarios", json={"nombre": "Sara Ruiz", "correo": "sara@umb.edu.co",
                                    "clave": CLAVE_OK}).get_json()["id"]
    h_user = login(c, "sara@umb.edu.co")
    h_admin = login(c, "admin@umb.edu.co")
    assert c.delete(f"/usuarios/{uid}", headers=h_admin).status_code == 204
    assert c.get(f"/usuarios/{uid}", headers=h_user).status_code == 401
