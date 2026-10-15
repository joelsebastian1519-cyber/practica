"""API REST (Flask) del módulo de gestión de usuarios.

Ejecutar:  python -m gestion_usuarios.api   (desde la carpeta src)
"""
import secrets

from flask import Flask, jsonify, request

from .repositorio import RepositorioUsuarios, Usuario
from .servicio import (ErrorAutenticacion, ErrorConflicto, ErrorNoEncontrado,
                       ErrorPermisos, ErrorValidacion, ServicioUsuarios)


def _a_json(u: Usuario) -> dict:
    # Nunca se expone el hash de la contraseña.
    return {"id": u.id, "nombre": u.nombre, "correo": u.correo, "rol": u.rol,
            "bloqueado": u.bloqueado}


def crear_app(ruta_bd: str = ":memory:") -> Flask:
    app = Flask(__name__)
    servicio = ServicioUsuarios(RepositorioUsuarios(ruta_bd))
    sesiones: dict[str, int] = {}          # token -> id de usuario
    app.config["SERVICIO"] = servicio

    def usuario_actual() -> Usuario:
        cabecera = request.headers.get("Authorization", "")
        token = cabecera.removeprefix("Bearer ").strip()
        if token not in sesiones:
            raise ErrorAutenticacion("Token ausente o inválido.")
        try:
            return servicio.obtener(sesiones[token])
        except ErrorNoEncontrado:
            sesiones.pop(token, None)
            raise ErrorAutenticacion("La sesión ya no es válida.")

    @app.errorhandler(ErrorValidacion)
    def _e400(e):
        return jsonify(error="validacion", detalles=e.errores), 400

    @app.errorhandler(ErrorAutenticacion)
    def _e401(e):
        return jsonify(error=str(e)), 401

    @app.errorhandler(ErrorPermisos)
    def _e403(e):
        return jsonify(error=str(e)), 403

    @app.errorhandler(ErrorNoEncontrado)
    def _e404(e):
        return jsonify(error=str(e)), 404

    @app.errorhandler(ErrorConflicto)
    def _e409(e):
        return jsonify(error=str(e)), 409

    @app.post("/usuarios")
    def registrar():
        datos = request.get_json(silent=True) or {}
        # El rol enviado por un cliente anónimo se ignora: siempre 'estandar'.
        u = servicio.registrar(datos.get("nombre", ""), datos.get("correo", ""),
                               datos.get("clave", ""))
        return jsonify(_a_json(u)), 201

    @app.post("/login")
    def login():
        datos = request.get_json(silent=True) or {}
        u = servicio.autenticar(datos.get("correo", ""), datos.get("clave", ""))
        token = secrets.token_urlsafe(24)
        sesiones[token] = u.id
        return jsonify(token=token, usuario=_a_json(u)), 200

    @app.get("/usuarios")
    def listar():
        return jsonify([_a_json(u) for u in servicio.listar(usuario_actual())])

    @app.get("/usuarios/<int:uid>")
    def obtener(uid):
        actor = usuario_actual()
        if actor.rol != "administrador" and actor.id != uid:
            raise ErrorPermisos("No tiene permisos sobre este usuario.")
        return jsonify(_a_json(servicio.obtener(uid)))

    @app.put("/usuarios/<int:uid>")
    def editar(uid):
        datos = request.get_json(silent=True) or {}
        u = servicio.editar_perfil(usuario_actual(), uid, datos.get("nombre"),
                                   datos.get("correo"))
        return jsonify(_a_json(u))

    @app.put("/usuarios/<int:uid>/rol")
    def cambiar_rol(uid):
        datos = request.get_json(silent=True) or {}
        return jsonify(_a_json(servicio.cambiar_rol(usuario_actual(), uid,
                                                    datos.get("rol", ""))))

    @app.delete("/usuarios/<int:uid>")
    def eliminar(uid):
        servicio.eliminar(usuario_actual(), uid)
        for t, i in list(sesiones.items()):
            if i == uid:
                sesiones.pop(t)
        return "", 204

    return app


if __name__ == "__main__":  # pragma: no cover
    crear_app("usuarios.db").run(debug=True)
