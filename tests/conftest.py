import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from gestion_usuarios.api import crear_app  # noqa: E402
from gestion_usuarios.repositorio import RepositorioUsuarios  # noqa: E402
from gestion_usuarios.servicio import ServicioUsuarios  # noqa: E402

CLAVE_OK = "Segura#2026"


@pytest.fixture
def servicio():
    s = ServicioUsuarios(RepositorioUsuarios(":memory:"))
    yield s
    s.repo.conexion.close()


@pytest.fixture
def admin(servicio):
    return servicio.registrar("Ana Admin", "admin@umb.edu.co", CLAVE_OK, "administrador")


@pytest.fixture
def estandar(servicio):
    return servicio.registrar("Luis Usuario", "luis@umb.edu.co", CLAVE_OK)


@pytest.fixture
def app_cliente():
    app = crear_app(":memory:")
    app.config["SERVICIO"].registrar("Ana Admin", "admin@umb.edu.co", CLAVE_OK, "administrador")
    yield app.test_client()
    app.config["SERVICIO"].repo.conexion.close()


def login(cliente, correo, clave=CLAVE_OK):
    r = cliente.post("/login", json={"correo": correo, "clave": clave})
    return {"Authorization": f"Bearer {r.get_json()['token']}"} if r.status_code == 200 else None
