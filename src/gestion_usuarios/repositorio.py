"""Capa de acceso a datos (SQLite). Se puede usar ':memory:' en pruebas."""
import sqlite3
from dataclasses import dataclass


@dataclass
class Usuario:
    id: int
    nombre: str
    correo: str
    hash_clave: str
    rol: str
    intentos_fallidos: int = 0
    bloqueado: bool = False


_ESQUEMA = """
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    correo TEXT NOT NULL UNIQUE,
    hash_clave TEXT NOT NULL,
    rol TEXT NOT NULL CHECK (rol IN ('estandar', 'administrador')),
    intentos_fallidos INTEGER NOT NULL DEFAULT 0,
    bloqueado INTEGER NOT NULL DEFAULT 0
);
"""


class RepositorioUsuarios:
    def __init__(self, ruta_bd: str = ":memory:"):
        self.conexion = sqlite3.connect(ruta_bd, check_same_thread=False)
        self.conexion.row_factory = sqlite3.Row
        self.conexion.executescript(_ESQUEMA)

    @staticmethod
    def _a_usuario(fila) -> Usuario | None:
        if fila is None:
            return None
        return Usuario(
            id=fila["id"], nombre=fila["nombre"], correo=fila["correo"],
            hash_clave=fila["hash_clave"], rol=fila["rol"],
            intentos_fallidos=fila["intentos_fallidos"],
            bloqueado=bool(fila["bloqueado"]),
        )

    def crear(self, nombre: str, correo: str, hash_clave: str, rol: str) -> Usuario:
        with self.conexion:
            cursor = self.conexion.execute(
                "INSERT INTO usuarios (nombre, correo, hash_clave, rol) VALUES (?, ?, ?, ?)",
                (nombre, correo, hash_clave, rol),
            )
        return self.obtener_por_id(cursor.lastrowid)

    def obtener_por_id(self, usuario_id: int) -> Usuario | None:
        fila = self.conexion.execute(
            "SELECT * FROM usuarios WHERE id = ?", (usuario_id,)
        ).fetchone()
        return self._a_usuario(fila)

    def obtener_por_correo(self, correo: str) -> Usuario | None:
        fila = self.conexion.execute(
            "SELECT * FROM usuarios WHERE correo = ?", (correo,)
        ).fetchone()
        return self._a_usuario(fila)

    def listar(self) -> list[Usuario]:
        filas = self.conexion.execute("SELECT * FROM usuarios ORDER BY id").fetchall()
        return [self._a_usuario(f) for f in filas]

    def actualizar(self, usuario: Usuario) -> Usuario:
        with self.conexion:
            self.conexion.execute(
                """UPDATE usuarios SET nombre = ?, correo = ?, hash_clave = ?, rol = ?,
                   intentos_fallidos = ?, bloqueado = ? WHERE id = ?""",
                (usuario.nombre, usuario.correo, usuario.hash_clave, usuario.rol,
                 usuario.intentos_fallidos, int(usuario.bloqueado), usuario.id),
            )
        return self.obtener_por_id(usuario.id)

    def eliminar(self, usuario_id: int) -> bool:
        with self.conexion:
            cursor = self.conexion.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))
        return cursor.rowcount == 1
