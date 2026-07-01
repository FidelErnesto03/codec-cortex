# Derivar docstrings desde CORTEX

**Perfil: HCORTEX-HOWTO**

| Objetivo | Comando |
|---|---|
| Generar una docstring | `cortex docstring canonicalize` |
| Generar todas | `cortex docstring --all` |
| Usar otra fuente | `cortex docstring canonicalize --docs-root docs/cortex/api` |
| Salida JSON | `cortex docstring canonicalize --format json` |

## Flujo

1. Editar `docs/cortex/api/<command>.cortex`.
2. Ejecutar `cortex verify docs/cortex/api/<command>.cortex --strict`.
3. Ejecutar `cortex docstring <command>`.
4. Revisar que la ayuda refleje argumentos, estado y límites.

## Criterio

| Regla | Aplicación |
|---|---|
| No duplicar documentación | Actualizar primero la fuente `.cortex` |
| No instalar sin revisar | Comparar diff antes de persistir cambios en código |
