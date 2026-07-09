# Bug Report: `cortex add` rechaza sigilos declarados en $0 (E003_UNKNOWN_SIGIL)

**Reportado por:** alfred (steward NOMOS)
**Fecha:** 2026-07-04
**Severidad:** Media
**Componente:** `cortex add` / parser de $0
**Versión CODEC-CORTEX:** 0.4.0

---

## Síntoma

`cortex add --sigil SES` falla con:
```
error: [E003_UNKNOWN_SIGIL] (sigil SES) sigil 'SES' not declared in $0
```

A pesar de que `SES` está documentado en `$0` del brain.cortex destino.

## Evidencia

**Brain.cortex donde falla:** `ENVX_OPER/.cortex/brain.cortex`
- 212 líneas, 110 entradas, 0 errores en `cortex verify --strict`
- `$0: UNIVERSAL GLOSSARY` con tabla de 15 sigilos incluyendo `SES`
- Bloque `<!-- CODEC-CORTEX ... -->` presente antes de `$0`

**Brain.cortex donde funciona:** `NOMOS/.cortex/brain.cortex`
- 73 líneas, 32 entradas
- `$0: MINIMAL LOCAL GLOSSARY` con tabla de sigilos
- **Sin** bloque `<!-- CODEC-CORTEX -->` antes de `$0`
- `cortex add --sigil SES` encuentra el sigilo (falla después por E024, no por E003)

## Causa probable

El parser de `cortex add` no reconoce las declaraciones de sigilos en `$0` cuando:

1. El archivo tiene un bloque HTML `<!-- ... -->` antes de la sección `$0`
2. El formato del glosario usa comentarios (`# Sigil | Name | ...`) en vez de declaraciones activas

`cortex verify --strict` SÍ reconoce estas declaraciones (W_EMPTY_GLOSSARY es solo warning, pasa la validación), pero `cortex add` no. Hay inconsistencia entre ambos comandos.

## Pasos para reproducir

```bash
# 1. Verificar que el brain pasa validation
cortex verify --strict brain.cortex
# → 0 errores

# 2. Intentar agregar entrada con sigilo declarado
cortex add brain.cortex --section '$3' --sigil SES --name test --value 'test:"ok"'
# → error: E003_UNKNOWN_SIGIL
```

## Impacto

- `brain.update` (handler MCP de NOMOS) falla al escribir en brains que tienen `<!-- CODEC-CORTEX -->` header
- Cualquier agente que use `cortex add` contra brains con header HTML no puede agregar entradas
- Workaround: editar brain.cortex directamente con `patch` o `write_file`

## Reproducibilidad

- Constante: 100% de los casos con header `<!-- CODEC-CORTEX -->` antes de `$0`
- No se reproduce en brains sin ese header

## Workaround actual

Editar el brain.cortex directamente (patch) en vez de usar `cortex add`.
