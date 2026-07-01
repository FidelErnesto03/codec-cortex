---
view: reference
reversible: true
profile: HCORTEX-REF
source: skill/cortex/SKILL.md §0, docs/cortex/api/*
mode: AUDIT
---

# Referencia HCORTEX

> **source:** skill/cortex/SKILL.md §0:canonical_sigils · docs/cortex/api/*

Consulta rápida de sigilos, comandos CLI, perfiles, códigos de error y convenciones.

---

## Sigilos

| Sigilo | Tipo | Riesgo | Corteza | Descripción | source |
|:------:|:----:|:------:|:-------:|-------------|--------|
| IDN | attrs | B | Semántica | Identidad de proyecto/artefacto | `$0:IDN:identity` |
| DOM | attrs | B | Semántica | Alcance, dominio, contexto | `$0:DOM:domain` |
| KNW | attrs | B | Semántica | Conocimiento base o promovido | `$0:KNW:knowledge` |
| REF | attrs | B | Semántica | Referencia a documento | `$0:REF:reference` |
| TAG | attrs | B | Semántica | Metadatos de clasificación | `$0:TAG:tag` |
| ! | attrs | H | Prefrontal | Regla operacional compacta | `$0:!:rule` |
| AXM | cuerpo | H | Prefrontal | Principio no negociable | `$0:AXM:axiom` |
| CNST | attrs | H | Prefrontal | Restricción dura | `$0:CNST:constraint` |
| CLAIM | attrs | M | Prefrontal | Afirmación verificable | `$0:CLAIM:claim` |
| LIM | attrs | M | Prefrontal | Límite explícito | `$0:LIM:limit` |
| AUD | attrs | M | Prefrontal | Registro de auditoría | `$0:AUD:audit` |
| RSK | attrs | M | Prefrontal | Riesgo con mitigación | `$0:RSK:risk` |
| FCS | attrs | H | Trabajo | Anclaje de atención activo | `$0:FCS:focus` |
| OBJ | attrs | H | Trabajo | Meta con criterio de éxito | `$0:OBJ:objective` |
| WRK | attrs | B | Trabajo | Estado de ejecución | `$0:WRK:work` |
| STP | attrs | M | Trabajo | Próxima acción inmediata | `$0:STP:step` |
| NXT | attrs | M | Trabajo | Acción en cola | `$0:NXT:next` |
| SES | attrs | M | Episódica | Episodio comprimido I/O/R | `$0:SES:session` |
| LNG | attrs | M | Episódica | Lección aprendida | `$0:LNG:lesson` |
| DIAG | bloque | M | Episódica/Visual | Diagrama PUML | `$0:DIAG:diagram` |
| HDL | attrs-pos | M | Semántica | Handler operacional | `$0:HDL:handler` |
| PFL | attrs | M | Prefrontal | Antipatrón conocido | `$0:PFL:pitfall` |
| DEP | attrs | M | Semántica | Dependencia | `$0:DEP:dependency` |
| DESC | cuerpo | B | Semántica | Descripción textual | `$0:DESC:description` |
| ERR | attrs | M | Prefrontal | Error conocido | `$0:ERR:error` |

---

## Comandos CLI

| Comando | Desde | Descripción | source |
|---------|:-----:|-------------|--------|
| `cortex --version` | 0.3.0 | Mostrar versión | `docs/cortex/api/canonicalize.cortex` |
| `cortex new` | 0.3.0 | Crear nuevo `.cortex` | `docs/cortex/api/canonicalize.cortex` |
| `cortex inspect` | 0.3.2 | Mostrar secciones, entries, VIEW | `docs/cortex/api/canonicalize.cortex` |
| `cortex verify` | 0.3.0 | Validar estructura | `docs/cortex/api/verify.cortex` |
| `cortex verify-view` | 0.3.2 | Cobertura VIEW | `docs/cortex/api/verify.cortex` |
| `cortex verify --signature` | 0.3.4 | Verificación integridad | `docs/cortex/api/verify.cortex` |
| `cortex roundtrip` | 0.3.2 | Roundtrip byte-idéntico | `docs/cortex/api/convert.cortex` |
| `cortex roundtrip-bidir` | 0.3.2 | Roundtrip CORTEX⇄HCORTEX | `docs/cortex/api/convert.cortex` |
| `cortex convert` | 0.3.2 | Convertir formatos | `docs/cortex/api/convert.cortex` |
| `cortex compare` | 0.3.2 | Comparación estructural | `docs/cortex/api/convert.cortex` |
| `cortex canonicalize` | 0.3.2 | Normalizar estructura | `docs/cortex/api/canonicalize.cortex` |
| `cortex explain-loss` | 0.3.2 | Reportar pérdida | `docs/cortex/api/convert.cortex` |
| `cortex add` | 0.3.0 | Agregar entrada | `docs/cortex/api/canonicalize.cortex` |
| `cortex update` | 0.3.0 | Actualizar entrada | `docs/cortex/api/canonicalize.cortex` |
| `cortex delete` | 0.3.0 | Eliminar entrada | `docs/cortex/api/canonicalize.cortex` |
| `cortex move` | 0.3.0 | Mover entrada | `docs/cortex/api/canonicalize.cortex` |
| `cortex doctor` | 0.3.0 | Diagnóstico profundo | `docs/cortex/api/doctor.cortex` |
| `cortex doctor --scan-secrets` | 0.3.4 | Scan de secretos | `docs/cortex/api/doctor.cortex` |
| `cortex audit` | 0.3.4 | Gestión auditoría | `docs/cortex/api/audit.cortex` |
| `cortex recover` | 0.3.0 | Recuperar legacy | `docs/cortex/api/canonicalize.cortex` |
| `cortex docstring` | 0.3.5 | Generar docstrings | `docs/cortex/api/docstring.cortex` |
| `cortex benchmark` | 0.3.5 | Listar/inspeccionar suites | `docs/cortex/api/benchmark.cortex` |

---

## Perfiles HCORTEX

| Perfil | Presupuesto | P-levels | Cuándo | source |
|--------|:-----------:|:--------:|--------|--------|
| CORTEX-MIN | ~300t | P0 | Emergencia | `$9:KNW:profile_min` |
| CORTEX-RECOVERY | ~1Kt | P0-P2 | Reconexión | `$9:KNW:profile_recovery` |
| CORTEX-WORK | ~4Kt | P0-P3 | Operación diaria | `$9:KNW:profile_work` |
| CORTEX-FULL | ~8Kt | P0-P5 | Auditoría | `$9:KNW:profile_full` |

---

## Modos de render

| Modo | Source visible | Para | source |
|------|:--------------:|------|--------|
| READABLE | No | Lectura ejecutiva | `$11:KNW:hc_modes` |
| AUDIT | Sí | Trazabilidad | `$11:KNW:hc_modes` |
| RECOVERY | No (solo P0-P2) | Reconexión | `$11:KNW:hc_modes` |
| FULL | Sí | Exportación amplia | `$11:KNW:hc_modes` |

---

## Perfiles CORTEX-OUT

| Perfil | Bloques | Cuándo | source |
|--------|---------|--------|--------|
| OUT-MIN | Resultado + Acción | <500t | `$12:KNW:out_blocks` |
| OUT-WORK | Resultado + Criterio + Acción + Límite | Respuesta operativa | `$12:KNW:out_blocks` |
| OUT-AUDIT | Todos con trazabilidad | Verificación | `$12:KNW:out_blocks` |
| OUT-FULL | Todos expandidos | Sesión completa | `$12:KNW:out_blocks` |
| OUT-ERROR | Código + causa + recuperación | Error | `$12:KNW:out_blocks` |

---

## Códigos de error

| Código | Severidad | Descripción | source |
|:------:|:---------:|-------------|--------|
| E003 | Error | Sigilo desconocido | `!:extend_glossary` |
| E023 | Error | Violación Nivel 1 | `$5:CNST:sep_l1` |
| E024 | Error | Falta foco Nivel 2 | `$5:CNST:sep_l2` |
| E031 | Error | Secreto en claro | `!:secret_scan` |
| E032 | Error | Sigilo crítico incompleto | `$7:CNST:contract_*` |
| E034 | Error | Campo crítico vacío | `$7:CNST:contract_*` |
| E_VIEW_* | Error | Violación VIEW | `$13:VIEW:*` |
| W_VIEW_* | Warning | Problema VIEW | `$13:VIEW:*` |
| W_HCORTEX_DISPLAY_ONLY | Warning | HCORTEX no reversible | `$11:KNW:hc_modes` |

---

## Microtokens

| Token | Expansión | source | Token | Expansión | source |
|:-----:|:---------|--------|:-----:|:---------|--------|
| cur | current | `$0:micro_cur` | min | minimum | `$0:micro_min` |
| pln | planned | `$0:micro_pln` | rec | recovery | `$0:micro_rec` |
| fut | future | `$0:micro_fut` | wrk | work | `$0:micro_wrk` |
| blk | blocked | `$0:micro_blk` | full | full | `$0:micro_full` |
| ok | success | `$0:micro_ok` | fail | failure | `$0:micro_fail` |
| d1 | decode | `$0:micro_d1` | d2 | detect | `$0:micro_d2` |
| d3 | decay | `$0:micro_d3` | c1 | .cortex | `$0:micro_c1` |
| c2 | HCORTEX | `$0:micro_c2` | v1 | validate | `$0:micro_v1` |
| v2 | verify | `$0:micro_v2` | p1 | promote | `$0:micro_p1` |

---

## Convenciones

| Convención | Regla | source |
|------------|-------|--------|
| Sigilos | MAYÚSCULAS (FCS, OBJ), excepto `!` | `!:id_format` |
| Instancias | snake_case (FCS:primary) | `!:id_format` |
| Glosario primero | `$0` como primera sección | `!section_normalize` |
| Fuente de verdad | `docs/cortex/api/` | `!:docs_source_of_truth` |
| Nombres canónicos | Sin prefijos de versión | `!:canonical_names` |

---

## Jerarquía de fuentes

| Fuente | Ubicación | Formato | Verif. | source |
|--------|-----------|:-------:|:------:|--------|
| Protocolo | `skill/cortex/SKILL.md` | CORTEX | ✅ | `$1:REF:art_skill_cortex` |
| Vista humana | `skill/hcortex/SKILL.md` | HCORTEX | ✅ | `$1:REF:art_skill_hcortex` |
| API CLI | `docs/cortex/api/*.cortex` | CORTEX | ✅ | `docs/cortex/api/README.md` |
| Tutoriales | `docs/es/hcortex/tutorials/` | HCORTEX (disp) | ❌ | Este archivo |
| How-to | `docs/es/hcortex/how-to/` | HCORTEX (disp) | ❌ | Este archivo |
| Explicaciones | `docs/es/hcortex/explanations/` | HCORTEX (disp) | ❌ | Este archivo |
| Referencia | Este archivo | HCORTEX (ref) | ✅ | Este archivo |
