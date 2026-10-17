# Plan de pruebas — Módulo de Gestión de Usuarios (proyecto de semestre)

Basado en la estructura de ISO/IEC/IEEE 29119-3. Versión completa en el informe de laboratorio.

1. **Objetivo:** garantizar que el registro, la autenticación, la edición de perfil, la gestión de roles y la eliminación de cuentas funcionen de forma correcta y segura.
2. **Alcance:** registro, inicio de sesión (con bloqueo por intentos), perfil, roles (estándar / administrador), eliminación. Fuera de alcance: recuperación de contraseña por correo, rendimiento con carga real.
3. **Estrategia:** pirámide de pruebas — unitarias (validadores, seguridad), integración (servicio + SQLite), sistema E2E (API REST), seguridad y regresión automatizadas con pytest; pruebas exploratorias manuales con Postman.
4. **Técnicas de diseño:** partición de equivalencia, valores límite, tablas de decisión (permisos por rol), transición de estados (bloqueo de cuenta).
5. **Casos:** 36 casos (CP-01 a CP-36) en `casos_de_prueba.csv`, implementados en 68 pruebas automatizadas (con parametrización).
6. **Entorno:** Python 3.11+, Flask 3, SQLite en memoria, pytest + pytest-cov; GitHub como repositorio.
7. **Criterios de entrada:** requisitos aprobados, entorno listo, casos diseñados.
8. **Criterios de salida:** ≥95 % de casos ejecutados, 100 % de defectos críticos/altos cerrados, cobertura de líneas ≥85 %, informe entregado.
9. **Resultado:** 68/68 pruebas aprobadas, cobertura 99 %, 1 defecto alto encontrado y cerrado (DEF-001).

Ejecutar: `pip install -r requirements.txt` y luego `pytest --cov=gestion_usuarios`.
