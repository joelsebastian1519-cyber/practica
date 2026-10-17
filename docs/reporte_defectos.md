# Registro de defectos

| Campo | DEF-001 |
|---|---|
| Título | El registro acepta un correo duplicado si se escribe con mayúsculas o espacios |
| Módulo | Registro de usuarios (`servicio.registrar`) |
| Detectado por | Caso CP-11 (`test_cp11_def001_correo_duplicado_con_mayusculas`) |
| Fecha | 16/10/2026 |
| Severidad | Alta — permite cuentas duplicadas y rompe la unicidad del correo |
| Prioridad | Alta |
| Pasos | 1) Registrar `luis@umb.edu.co`. 2) Registrar `  LUIS@UMB.EDU.CO `. |
| Esperado | HTTP 409 / `ErrorConflicto` |
| Obtenido | El segundo registro se crea con éxito |
| Causa raíz | Se aplicaba `strip()` pero no `lower()` antes de consultar duplicados |
| Corrección | Uso de `validadores.normalizar_correo()` (rama `fix/DEF-001-correo-mayusculas`, PR #4) |
| Verificación | CP-11 pasa; suite completa 68/68; se conserva como prueba de regresión |
| Estado | Cerrado |

Ciclo de vida aplicado: Nuevo → Asignado → En corrección → Corregido → Verificado → Cerrado.
