# Política de dependencias e imports — CORTEX Core

**Document ID:** `CCX-DEP-POLICY-0001`  
**Status:** `approved`  
**Date:** `2026-07-16`

## Regla principal

Las dependencias son unidireccionales:

```text
cortex-standard
      ↓
codec-cortex
      ↓
profiles / adapters / tooling
      ↓
runtime / learning / ArqUX
```

Queda prohibido:

```text
codec-cortex -> cortex-profiles
codec-cortex -> cortex-learning
codec-cortex -> cortex-runtime
codec-cortex -> ArqUX
codec-cortex -> agent ontology
```

## Capas permitidas en `codec-cortex`

```text
cortex.model
cortex.syntax
cortex.parser
cortex.writer
cortex.canonical
cortex.hcortex
cortex.validate
cortex.codec
cortex.profiles   # interfaces de carga, nunca perfiles oficiales
cortex.conformance
cortex.cli
cortex.api
```

## Capas externas

```text
cortex-crud
cortex-query
cortex-editor
cortex-sign
cortex-migrate
cortex-lsp
cortex-mcp
cortex-learning
cortex-runtime
cortex-profiles
arqux
```

## Reglas ejecutables

1. Ningún módulo del núcleo puede importar paquetes externos del ecosistema.
2. Ningún nombre de sigilo de perfil puede aparecer como requisito duro del parser.
3. La validación de perfiles se activa explícitamente y se carga por interfaz.
4. Una extensión desconocida se preserva o genera diagnóstico; nunca se descarta.
5. El núcleo debe instalarse y ejecutar su corpus sin perfiles.
6. Eliminar todos los repositorios externos no debe alterar parseo, escritura ni canonicalización.
7. La canonicalización no consulta red, base de datos, runtime ni LLM.
8. Los adaptadores dependen del núcleo; el núcleo no depende de adaptadores.
9. Los tests del núcleo no pueden requerir `FCS`, `LNG`, `KNW`, `SES`, `brain` o `workspace`.
10. Los ejemplos de perfiles se prueban en `cortex-profiles`, no en el corpus normativo base.

## Gate automático propuesto

El repositorio limpio deberá incluir una prueba que falle ante imports prohibidos. Patrón conceptual:

```text
scan src/cortex
deny imports:
  cortex_learning
  cortex_runtime
  cortex_profiles_official
  arqux
  agent_profile
```

También deberá existir una prueba de instalación mínima:

```text
clean environment
install codec-cortex
remove all optional profile packages
run core conformance corpus
```

## Excepciones

No existen excepciones implícitas. Toda excepción requiere una propuesta formal, análisis de compatibilidad, cambio de corpus y aprobación arquitectónica.
