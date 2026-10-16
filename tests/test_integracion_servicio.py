"""Pruebas de INTEGRACIÓN: servicio de negocio + repositorio SQLite real."""
import pytest

from gestion_usuarios.servicio import (ErrorAutenticacion, ErrorConflicto, ErrorNoEncontrado,
                                       ErrorPermisos, ErrorValidacion)

from conftest import CLAVE_OK

pytestmark = pytest.mark.integracion


# --- Registro ---------------------------------------------------------------
def test_cp08_registro_exitoso_persiste_en_bd(servicio):
    u = servicio.registrar("María Gómez", "maria@umb.edu.co", CLAVE_OK)
    assert u.id is not None and u.rol == "estandar"
    assert servicio.repo.obtener_por_correo("maria@umb.edu.co").nombre == "María Gómez"


def test_cp09_registro_con_datos_invalidos_reporta_todos_los_errores(servicio):
    with pytest.raises(ErrorValidacion) as exc:
        servicio.registrar("A", "malo", "123", "root")
    assert len(exc.value.errores) >= 4
    assert servicio.repo.listar() == []


def test_cp10_registro_correo_duplicado(servicio, estandar):
    with pytest.raises(ErrorConflicto):
        servicio.registrar("Otro", "luis@umb.edu.co", CLAVE_OK)


@pytest.mark.regresion
def test_cp11_def001_correo_duplicado_con_mayusculas(servicio, estandar):
    """Regresión DEF-001: 'LUIS@UMB.EDU.CO' se aceptaba como correo nuevo."""
    with pytest.raises(ErrorConflicto):
        servicio.registrar("Otro", "  LUIS@UMB.EDU.CO ", CLAVE_OK)


# --- Autenticación ----------------------------------------------------------
def test_cp12_login_exitoso(servicio, estandar):
    assert servicio.autenticar("luis@umb.edu.co", CLAVE_OK).id == estandar.id


def test_cp13_login_clave_incorrecta(servicio, estandar):
    with pytest.raises(ErrorAutenticacion, match="Credenciales inválidas"):
        servicio.autenticar("luis@umb.edu.co", "Mala#2026x")


def test_cp14_login_correo_inexistente_mismo_mensaje(servicio):
    with pytest.raises(ErrorAutenticacion, match="Credenciales inválidas"):
        servicio.autenticar("nadie@umb.edu.co", CLAVE_OK)


@pytest.mark.seguridad
def test_cp15_bloqueo_tras_tres_intentos(servicio, estandar):
    for _ in range(3):
        with pytest.raises(ErrorAutenticacion):
            servicio.autenticar("luis@umb.edu.co", "Mala#2026x")
    with pytest.raises(ErrorAutenticacion, match="bloqueada"):
        servicio.autenticar("luis@umb.edu.co", CLAVE_OK)   # ni con la clave correcta


def test_cp16_login_correcto_reinicia_contador(servicio, estandar):
    for _ in range(2):
        with pytest.raises(ErrorAutenticacion):
            servicio.autenticar("luis@umb.edu.co", "Mala#2026x")
    servicio.autenticar("luis@umb.edu.co", CLAVE_OK)
    assert servicio.obtener(estandar.id).intentos_fallidos == 0


def test_cp17_admin_desbloquea_cuenta(servicio, admin, estandar):
    for _ in range(3):
        with pytest.raises(ErrorAutenticacion):
            servicio.autenticar("luis@umb.edu.co", "Mala#2026x")
    servicio.desbloquear(admin, estandar.id)
    assert servicio.autenticar("luis@umb.edu.co", CLAVE_OK).id == estandar.id


# --- Perfil -----------------------------------------------------------------
def test_cp18_usuario_edita_su_perfil(servicio, estandar):
    u = servicio.editar_perfil(estandar, estandar.id, nombre="Luis Alberto",
                               correo="LuisA@umb.edu.co")
    assert (u.nombre, u.correo) == ("Luis Alberto", "luisa@umb.edu.co")


def test_cp19_usuario_no_edita_perfil_ajeno(servicio, admin, estandar):
    with pytest.raises(ErrorPermisos):
        servicio.editar_perfil(estandar, admin.id, nombre="Hackeado")


def test_cp20_editar_a_correo_existente(servicio, admin, estandar):
    with pytest.raises(ErrorConflicto):
        servicio.editar_perfil(estandar, estandar.id, correo="admin@umb.edu.co")


def test_cp20b_editar_con_datos_invalidos(servicio, estandar):
    with pytest.raises(ErrorValidacion):
        servicio.editar_perfil(estandar, estandar.id, nombre="X1")


# --- Roles ------------------------------------------------------------------
def test_cp21_admin_cambia_rol(servicio, admin, estandar):
    assert servicio.cambiar_rol(admin, estandar.id, "administrador").rol == "administrador"


@pytest.mark.seguridad
def test_cp22_estandar_no_cambia_roles(servicio, estandar):
    with pytest.raises(ErrorPermisos):
        servicio.cambiar_rol(estandar, estandar.id, "administrador")


def test_cp22b_rol_invalido(servicio, admin, estandar):
    with pytest.raises(ErrorValidacion):
        servicio.cambiar_rol(admin, estandar.id, "superusuario")


def test_cp22c_estandar_no_lista_ni_desbloquea(servicio, estandar):
    with pytest.raises(ErrorPermisos):
        servicio.listar(estandar)
    with pytest.raises(ErrorPermisos):
        servicio.desbloquear(estandar, estandar.id)


# --- Eliminación ------------------------------------------------------------
def test_cp23_usuario_elimina_su_cuenta(servicio, estandar):
    servicio.eliminar(estandar, estandar.id)
    with pytest.raises(ErrorNoEncontrado):
        servicio.obtener(estandar.id)


def test_cp24_no_eliminar_ultimo_admin(servicio, admin):
    with pytest.raises(ErrorPermisos, match="último administrador"):
        servicio.eliminar(admin, admin.id)


def test_cp25_eliminar_inexistente(servicio, admin):
    with pytest.raises(ErrorNoEncontrado):
        servicio.eliminar(admin, 999)
