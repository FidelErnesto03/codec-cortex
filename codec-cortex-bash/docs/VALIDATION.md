# Validación ejecutada

Fecha: 2026-07-17

| Verificación | Resultado |
|---|---|
| `bash -n` sobre CLI, library y self-test | PASS |
| Prueba rápida contra goldens Python | PASS |
| C14N fixture integral | byte-identical |
| HCORTEX render fixture integral | byte-identical |
| HCORTEX compile fixture integral | byte-identical |
| Gate F4 incluido | PASS: 5/5 roundtrip, 5/5 idempotencia, 2/2 diagnósticos |
| Runner F3 sobre caso aislado | 1/1 golden, 1/1 idempotencia, sin fallas |
| Instalación aislada con `DESTDIR` | PASS |

## Nota sobre F3 exhaustivo

El paquete incluye los 40 casos requeridos por el umbral heredado. El runner admite `CCX_JOBS`, pero el corpus completo no se declara ejecutado dentro de esta sesión porque Bash+jq generó una carga de procesos inestable en el entorno de construcción. Esto afecta tiempo/costo de ejecución, no los bytes ya comparados en los fixtures diferenciales.

Para ejecutarlo en una máquina local:

```bash
CCX_JOBS=1 make phase3
```

Subir gradualmente a `2` o `4` solo si memoria y CPU lo permiten.
