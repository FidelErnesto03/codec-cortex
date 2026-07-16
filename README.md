# CODEC-CORTEX

Representación canónica, compacta y autocontenida de contexto para agentes IA.

Este repositorio es el estándar abierto y su implementación de referencia.
CODEC-CORTEX es un **codec determinista** (parse, encode, decode, canonicalize,
validate, to/from HCORTEX). No es un runtime, motor de aprendizaje, ni framework
de gobierno. Esos sistemas consumen CORTEX como estándar externo.

## Estado

- Fase: 0 completada (raíz limpia, legacy congelado).
- Estándar: en constitución (ver `governance/`).
- Línea experimental v0.6.x: preservada en rama `legacy/v0.6.x` (inmutable).

## Dominios

| Directorio | Autoridad | Descripción |
|---|---|---|
| `standard/` | normativa | Especificación, gramática, schemas |
| `implementations/python/` | derivada | Implementación de referencia (placeholder en F0) |
| `profles/` | extensión | Perfiles opcionales (desacoplados) |
| `conformance/` | evidencia | Corpus y manifest de conformidad |
| `tooling/` | dev-only | Herramientas, no importadas por el Core |
| `governance/` | gobernanza | Charter, RFC, ADR, versionado, dependencias |
| `security/` | seguridad | Security policy, threat model |
| `docs/` | informativo | Documentación y transición |

## Dependencias

Unidireccionales: `standard → implementations → profiles/external consumers`.
El Core nunca importa learning, runtime, sesiones, ArqUX ni vocabularios cognitivos.
Ver `governance/DEPENDENCY_POLICY.md`.
