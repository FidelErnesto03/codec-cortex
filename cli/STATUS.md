# STATUS — codec-cortex v0.3.5

> Matriz de madurez de capacidades. Ningún claim debe presentarse como `current` sin evidencia reproducible.

**Spec de referencia:** `SKILL.md` v1.2.0-enterprise-candidate (`SKILL_canon.md` es el canon exacto del paquete).  
**Estado del paquete:** `enterprise-candidate` para el núcleo bidireccional CORTEX ⇄ HCORTEX, condicionado a mantener documentación y CI alineados.

> **v0.3.2 — Naming canónico:** los comandos `v2-*` se renombran a sus formas canónicas (`roundtrip`, `convert`, `roundtrip-bidir`, `compare`, `verify-view`, `explain-loss`, `canonicalize`, `inspect`). Los alias `v2-*` se mantienen como `deprecated` y serán removidos en v1.0.0.

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

## Capacidades (nombres canónicos v0.3.2 / v0.3.5 E3)

| Capacidad | Estado | Evidencia |
|---|---|---|
| Parser CORTEX → AST | `current` | `parse_cortex()`, `cortex inspect` |
| Writer AST → CORTEX | `current` | `cortex roundtrip` byte-identical |
| CORTEX → HCORTEX | `current` | `cortex convert --from cortex --to hcortex`, byte-identical contra `skill/hcortex/SKILL.md` |
| HCORTEX → CORTEX | `current` | `cortex convert --from hcortex --to cortex`, 266/266 entries |
| Roundtrip CORTEX → HCORTEX → CORTEX | `current` | `cortex roundtrip-bidir skill/cortex/SKILL.md`, AST-equivalent true, 0 diffs |
| Roundtrip HCORTEX → CORTEX → HCORTEX | `current` | `cortex roundtrip-bidir skill/hcortex/SKILL.md`, content-equivalent true, 0 diffs |
| VIEW directives | `current` | 44 VIEW en skill; 10/10 artefactos del corpus migrados a VIEW en v0.3.2 |
| Gate `reversible:true` | `current` | coverage 100%, cero errores, no display-only |
| Display-only no canónico | `current` | `W_HCORTEX_DISPLAY_ONLY` / `reversible:false` |
| Post-write validation | `current` | no escribe output si hay pérdida salvo force explícito |
| Recuperación de artefactos legacy | `current with known limits` | `cortex recover` legacy |
| Hash mismatch | `current` para hashes declarados | `E_VIEW_HASH_MISMATCH` cuando existe hash y no coincide |
| `--force-write-on-error` | `current` |  |
| `W_VIEW_HETEROGENEOUS_TARGET` | `current` |  |
| PUML / DIAG verbatim | `current` | bloques preservados en roundtrip canónico |
| Equivalence engine | `current` | byte, AST, semantic, content |
| `cortex compare` | `current` | reporta equivalencias y diffs (alias `v2-compare` deprecated) |
| `cortex verify-view` | `current` | coverage y reversibilidad (alias `v2-verify-view` deprecated) |
| `cortex explain-loss` | `current` | reporte de pérdida/no reversibilidad (alias `v2-explain-loss` deprecated) |
| `cortex canonicalize` (VIEW-aware) | `current` | v0.3.2: preserva estructura sin VIEW; canonicalización completa con VIEW; flag `--preserve` (alias `v2-canonicalize` deprecated) |
| `cortex inspect` | `current` | secciones, entries, VIEW, coverage (alias `v2-inspect` deprecated) |
| Alias `v2-*` (8 comandos) | `deprecated` | aceptados con WARNING; removidos en v1.0.0 |
| `cortex doctor` v2 | `planned` | no implementado como comando separado |
| JSON uniforme para todos los v2 | `planned` | no declarar como actual |
| Coverage por sigilo/sección/P-level | `planned` | coverage global actual; breakdown avanzado posterior |
| Source audit obligatorio P0/P1 | `planned` | source markers existen; enforcement audit completo posterior |
| MCP server | `future` | no implementado |
| Runtime promote/decay | `future` | no implementado |
| **Documentación central E3** | `current` | `docs/README.md` |
| **HCORTEX humano E3** | `current` | `docs/hcortex/tutorials/getting-started.md` |
| **API reference CORTEX E3** | `current` | `docs/cortex/api/*.cortex` |
| **Docstring derivada E3** | `current` | `cortex docstring canonicalize` |
| **Benchmark inventory E3** | `current` | `cortex benchmark --list` |
| **Coverage gate E3** | `current` | `.coveragerc` + CI |

## Artefactos canónicos

| Artefacto | Bytes | Estado |
|---|---:|---|
| `skill/cortex/SKILL.md` | 43,925 | CORTEX canónico, 14 secciones, 266 entries, 44 VIEW |
| `skill/hcortex/SKILL.md` | 47,186 | HCORTEX canónico, reversible, roundtrip válido |
| `benchmarks/v2.0.0/corpus/source/*.cortex` (10) | — | Corpus migrado a VIEW directives (v0.3.2); coverage 100% |

## Cambios por versión

- **0.3.5:** Protocolo de Documentación E3. `docs/README.md` central, estructura `docs/hcortex/` (tutorial, how-to, explicación, referencia), `docs/cortex/api/*.cortex` para referencia API autocontenida. Comandos `cortex docstring` y `cortex benchmark`. Entry point E3 con fallback histórico. Coverage gate 85%.
- **0.3.2:** naming canónico CLI (sin prefijo `v2-`); fix `cortex canonicalize` (B-01/B-05); flag `--preserve`; migración corpus a VIEW directives; renombramiento de métodos de benchmark; workflow operativo del agente (5 PUML, 4 reglas `!`, 5 perfiles CORTEX-OUT).
- **2.4.0:** núcleo bidireccional verificado. CORTEX ⇄ HCORTEX pasa con 0 diffs en artefactos canónicos; HCORTEX → CORTEX reconstruye 266/266 entries; VIEW 44/44; coverage 100%; paquete limpio; documentación alineada.
- **2.3.1:** release correctivo experimental. Tests empezaron a fallar honestamente cuando el roundtrip bidireccional no era real.
- **2.3.0:** primer parser inverso/encoder experimental; rechazado como bidireccional completo por pérdida estructural.
- **2.2.3:** gate de reversibilidad, distinción display vs canónico, documentación CORTEX/HCORTEX alineada.
- **2.2.2:** SKILL.md migrado con VIEW directives y endurecimiento de errores VIEW. `--force-write-on-error` y `W_VIEW_HETEROGENEOUS_TARGET`.
- **2.2.1:** HCORTEX-R deprecado, metadata VIEW completa y DIAG verbatim.

## No conformidades conocidas

| Área | Estado |
|---|---|
| `doctor` v2 | no implementado; usar `doctor` legacy + comandos canónicos |
| JSON v2 uniforme | pendiente |
| Hashes en los 44 VIEW markers canónicos | no presentes; la verificación opera cuando el hash está declarado |
| Breakdown avanzado de coverage | pendiente |
| Alias `v2-*` | `deprecated` desde v0.3.2; se remueven en v1.0.0 |
| `cortex docstring` | Lee `docs/cortex/api` desde el checkout del repositorio |
| `cortex benchmark` | Inventaria suites versionadas; no ejecuta modelos externos |
| Publicación v0.3.5 | Requiere tag `v0.3.5` |
