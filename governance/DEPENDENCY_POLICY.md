# Dependency Policy

## Direcciones permitidas
- `standard` → `implementations/*` (la implementación satisface el estándar)
- `conformance` → `implementations/*` (casos como datos de prueba)
- `implementations/*` API pública → `profiles/*` (perfiles dependen del codec)
- `tooling` → `standard|conformance|implementations|profiles` (solo desarrollo)

## Direcciones PROHIBIDAS (blocking)
- `implementations/*` → `learning` (motor de aprendizaje)
- `implementations/*` → `runtime|sessions|autonomous-memory`
- `implementations/*` → `ArqUX|project-governance`
- `standard` → `implementations|profiles|tooling` (autoridad no depende de derivados)
- Cualquier dependencia inversa a `standard → implementation → profiles`

## Reglas
- Ningún perfil concreto es requisito para parsear/escribir/canonicalizar/validar CORTEX base.
- El Core expone interfaces genéricas de extensión, no vocabularios oficiales obligatorios.
