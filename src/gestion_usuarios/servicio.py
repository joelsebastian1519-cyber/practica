"""Reglas de negocio del módulo de gestión de usuarios."""
from . import validadores as v
from .repositorio import RepositorioUsuarios, Usuario
from .seguridad import MAX_INTENTOS_FALLIDOS, generar_hash, verificar_clave


class ErrorValidacion(Exception):
    def __init__(self, errores: list[str]):
        super().__init__("; ".join(errores))
        self.errores = errores


class ErrorConflicto(Exception):
    """El recurso ya existe (p. ej. correo duplicado)."""


class ErrorNoEncontrado(Exception):
    pass


class ErrorAutenticacion(Exception):
    pass


class ErrorPermisos(Exception):
    pass


class ServicioUsuarios:
    def __init__(self, repositorio: RepositorioUsuarios):
        self.repo = repositorio

    # --- Registro -------------------------------------------------------
    def registrar(self, nombre: str, correo: str, clave: str, rol: str = "estandar") -> Usuario:
        errores = (v.validar_nombre(nombre) + v.validar_correo(correo)
                   + v.validar_clave(clave) + v.validar_rol(rol))
        if errores:
            raise ErrorValidacion(errores)
        correo = correo.strip()
        if self.repo.obtener_por_correo(correo):
            raise ErrorConflicto("Ya existe un usuario con ese correo.")
        return self.repo.crear(nombre.strip(), correo, generar_hash(clave), rol)

    # --- Autenticación ---------------------------------------------------
    def autenticar(self, correo: str, clave: str) -> Usuario:
        usuario = self.repo.obtener_por_correo(v.normalizar_correo(correo))
        # Mensaje genérico para no revelar si el correo existe.
        if usuario is None:
            raise ErrorAutenticacion("Credenciales inválidas.")
        if usuario.bloqueado:
            raise ErrorAutenticacion("La cuenta está bloqueada por intentos fallidos.")
        if not verificar_clave(clave, usuario.hash_clave):
            usuario.intentos_fallidos += 1
            if usuario.intentos_fallidos >= MAX_INTENTOS_FALLIDOS:
                usuario.bloqueado = True
            self.repo.actualizar(usuario)
            raise ErrorAutenticacion("Credenciales inválidas.")
        if usuario.intentos_fallidos:
            usuario.intentos_fallidos = 0
            usuario = self.repo.actualizar(usuario)
        return usuario

    # --- Perfil ------------------------------------------------------------
    def obtener(self, usuario_id: int) -> Usuario:
        usuario = self.repo.obtener_por_id(usuario_id)
        if usuario is None:
            raise ErrorNoEncontrado("Usuario no encontrado.")
        return usuario

    def editar_perfil(self, actor: Usuario, usuario_id: int, nombre: str | None = None,
                      correo: str | None = None) -> Usuario:
        self._verificar_propietario_o_admin(actor, usuario_id)
        usuario = self.obtener(usuario_id)
        errores = []
        if nombre is not None:
            errores += v.validar_nombre(nombre)
        if correo is not None:
            errores += v.validar_correo(correo)
        if errores:
            raise ErrorValidacion(errores)
        if correo is not None:
            correo = v.normalizar_correo(correo)
            otro = self.repo.obtener_por_correo(correo)
            if otro and otro.id != usuario_id:
                raise ErrorConflicto("Ya existe un usuario con ese correo.")
            usuario.correo = correo
        if nombre is not None:
            usuario.nombre = nombre.strip()
        return self.repo.actualizar(usuario)

    def cambiar_rol(self, actor: Usuario, usuario_id: int, nuevo_rol: str) -> Usuario:
        if actor.rol != "administrador":
            raise ErrorPermisos("Solo un administrador puede cambiar roles.")
        errores = v.validar_rol(nuevo_rol)
        if errores:
            raise ErrorValidacion(errores)
        usuario = self.obtener(usuario_id)
        usuario.rol = nuevo_rol
        return self.repo.actualizar(usuario)

    def desbloquear(self, actor: Usuario, usuario_id: int) -> Usuario:
        if actor.rol != "administrador":
            raise ErrorPermisos("Solo un administrador puede desbloquear cuentas.")
        usuario = self.obtener(usuario_id)
        usuario.bloqueado, usuario.intentos_fallidos = False, 0
        return self.repo.actualizar(usuario)

    # --- Eliminación -------------------------------------------------------
    def eliminar(self, actor: Usuario, usuario_id: int) -> None:
        self._verificar_propietario_o_admin(actor, usuario_id)
        self.obtener(usuario_id)
        if actor.id == usuario_id and actor.rol == "administrador":
            admins = [u for u in self.repo.listar() if u.rol == "administrador"]
            if len(admins) == 1:
                raise ErrorPermisos("No se puede eliminar al último administrador.")
        self.repo.eliminar(usuario_id)

    def listar(self, actor: Usuario) -> list[Usuario]:
        if actor.rol != "administrador":
            raise ErrorPermisos("Solo un administrador puede listar usuarios.")
        return self.repo.listar()

    @staticmethod
    def _verificar_propietario_o_admin(actor: Usuario, usuario_id: int) -> None:
        if actor.rol != "administrador" and actor.id != usuario_id:
            raise ErrorPermisos("No tiene permisos sobre este usuario.")
