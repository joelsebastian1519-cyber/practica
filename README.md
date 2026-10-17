# practica-control-versiones

Autores:
- [Nombre del estudiante 1] - Administrador del proyecto
- [Nombre del estudiante 2] - Colaborador

## Descripción del proyecto
Repositorio de la Guía 7 de Estándares y Métricas de Calidad de Software
(Pruebas y validación de software). Contiene el módulo de gestión de usuarios
del proyecto de semestre y su batería de pruebas automatizadas.

## Estructura
```
src/gestion_usuarios/   validadores, seguridad, repositorio (SQLite), servicio, api (Flask)
tests/                  pruebas unitarias, de integración y de sistema (pytest)
docs/                   plan de pruebas, casos de prueba, registro de defectos, reportes
log.txt                 historial generado con git log --oneline --graph --all
```

## Cómo ejecutar
```bash
pip install -r requirements.txt
pytest --cov=gestion_usuarios --cov-report=term-missing   # toda la suite
pytest -m unitaria        # solo unitarias (también: integracion, sistema, seguridad, regresion)
cd src && python -m gestion_usuarios.api                   # levantar la API en http://127.0.0.1:5000
```

## Resultado actual
68 pruebas aprobadas · cobertura 99 % · 1 defecto (DEF-001) detectado y cerrado.
