# STATUS — codec-cortex v2.4.0

> Matriz de madurez de capacidades. Ningún claim debe presentarse como `current` sin evidencia reproducible.

**Spec de referencia:** `SKILL.md` v1.2.0-enterprise-candidate (`SKILL_canon.md` es el canon exacto del paquete).  
**Estado del paquete:** `enterprise-candidate` para el núcleo bidireccional CORTEX ⇄ HCORTEX, condicionado a mantener documentación y CI alineados.

## Convenciones

| Estado | Significado |
|---|---|
| `current` | Implementado y verificado por pruebas/comandos reproducibles |
| `specification` | Definido normativamente; no necesariamente automatizado |
| `planned` | Diseñado para una versión posterior |
| `future` | Visión posterior sin implementación actual |
| `experimental` | Existe, pero no es estable/canónico |
| `deprecated` | Compatibilidad, no recomendado |

## Conceptos base

| Concepto | Rol | Estado |
|---|---|---|
| CORTEX | Representación densa nativa y fuente canónica operacional | `current` |
| HCORTEX / HUMAN-CORTEX | Representación humana densa reversible con VIEW/trazabilidad equivalente | `current` |
| VIEW | Contrato declarativo de correspondencia CORTEX ⇄ HCORTEX | `current` |
| CORTEX-OUT | Política de respuesta conversacional, fuera del codec | `specification` |

## Capacidades v2

| Capacidad | Estado | Evidencia |
|---|---|---|
| Parser CORTEX → AST | `current` | `parse_cortex()`, `v2-inspect` |
| Writer AST → CORTEX | `current` | `v2-roundtrip` byte-identical |
| CORTEX → HCORTEX | `current` (2.4.0) | `v2-convert --from cortex --to hcortex`, byte-identical contra `skill/hcortex/SKILL.md` |
| HCORTEX → CORTEX | `current` (2.4.0) | `v2-convert --from hcortex --to cortex`, 266/266 entries |
| Roundtrip CORTEX → HCORTEX → CORTEX | `current` (2.4.0) | `v2-roundtrip-bidir skill/cortex/SKILL.md`, AST-equivalent true, 0 diffs |
| Roundtrip HCORTEX → CORTEX → HCORTEX | `current` (2.4.0) | `v2-roundtrip-bidir skill/hcortex/SKILL.md`, content-equivalent true, 0 diffs |
| VIEW directives | `current` | 44 VIEW; coverage 100% |
| Gate `reversible:true` | `current` | coverage 100%, cero errores, no display-only |
| Display-only no canónico | `current` | `W_HCORTEX_DISPLAY_ONLY` / `reversible:false` |
| Post-write validation | `current` | no escribe output si hay pérdida salvo force explícito |
| Recuperación de artefactos legacy | `current with known limits` | `cortex recover` legacy |
| Hash mismatch | `current` para hashes declarados | `E_VIEW_HASH_MISMATCH` cuando existe hash y no coincide |
| `--force-write-on-error` | `current` |
| `W_VIEW_HETEROGENEOUS_TARGET` | `current` |
| PUML / DIAG verbatim | `current` | bloques preservados en roundtrip canónico |
| Equivalence engine | `current` | byte, AST, semantic, content |
| `v2-compare` | `current` | reporta equivalencias y diffs |
| `v2-verify-view` | `current` | coverage y reversibilidad |
| `v2-explain-loss` | `current` | reporte de pérdida/no reversibilidad |
| `v2-canonicalize` | `current` | normalización sin cambio semántico declarado |
| `v2-inspect` | `current` | secciones, entries, VIEW, coverage |
| `v2-doctor` | `planned` | no implementado como comando separado |
| JSON uniforme para todos los v2 | `planned` | no declarar como actual |
| Coverage por sigilo/sección/P-level | `planned` | coverage global actual; breakdown avanzado posterior |
| Source audit obligatorio P0/P1 | `planned` | source markers existen; enforcement audit completo posterior |
| MCP server | `future` | no implementado |
| Runtime promote/decay | `future` | no implementado |

## Artefactos canónicos

| Artefacto | Bytes | Estado |
|---|---:|---|
| `skill/cortex/SKILL.md` | 43,925 | CORTEX canónico, 14 secciones, 266 entries, 44 VIEW |
| `skill/hcortex/SKILL.md` | 47,186 | HCORTEX canónico, reversible, roundtrip válido |

## Cambios por versión

- **2.4.0:** núcleo bidireccional verificado. CORTEX ⇄ HCORTEX pasa con 0 diffs en artefactos canónicos; HCORTEX → CORTEX reconstruye 266/266 entries; VIEW 44/44; coverage 100%; paquete limpio; documentación alineada.
- **2.3.1:** release correctivo experimental. Tests empezaron a fallar honestamente cuando el roundtrip bidireccional no era real.
- **2.3.0:** primer parser inverso/encoder experimental; rechazado como bidireccional completo por pérdida estructural.
- **2.2.3:** gate de reversibilidad, distinción display vs canónico, documentación CORTEX/HCORTEX alineada.
- **2.2.2:** SKILL.md migrado con VIEW directives y endurecimiento de errores VIEW. `--force-write-on-error` y `W_VIEW_HETEROGENEOUS_TARGET`.
- **2.2.1:** HCORTEX-R deprecado, metadata VIEW completa y DIAG verbatim.

## No conformidades conocidas

| Área | Estado |
|---|---|
| `v2-doctor` | no implementado; usar `doctor` legacy + comandos v2 |
| JSON v2 uniforme | pendiente |
| Hashes en los 44 VIEW markers canónicos | no presentes; la verificación opera cuando el hash está declarado |
| Breakdown avanzado de coverage | pendiente |
