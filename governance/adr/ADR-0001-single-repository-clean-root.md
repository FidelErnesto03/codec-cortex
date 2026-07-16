# ADR-0001: Single Repository Clean-Root

## Estado
Aceptada (Fase 0).

## Contexto
El plan integral original proponía tres repositorios (cortex-standard,
codec-cortex, cortex-profiles). La orden CCX-F0-CLEAN-ROOT-ORDERS-001 revirtió
esa topología: un único repositorio oficial (`FidelErnesto03/codec-cortex`)
con dominios internos separados por directorios, paquetes, gates y CI.

## Decisión
Mantener un solo repositorio. La separación se implementa por fronteras
arquitectónicas verificables (CODEOWNERS, CI boundary check, dependency policy),
no por proliferación de repositorios.

## Consecuencias
- Se preservan nombre, URL, issues y estrellas del repositorio original.
- `main` nace de una rama huérfana (raíz sin padre).
- `legacy/v0.6.x` conserva la línea experimental congelada.
