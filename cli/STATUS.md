# STATUS — codec-cortex

> Estado de madurez de las capacidades declaradas por `codec-cortex`.
> Per el SKILL.md §0.3, ningún claim de capacidad puede presentarse como
> `current` sin verificación.
>
> **Spec de referencia:** `SKILL.md` v1.2.0-enterprise-candidate (MIT).
> El canon exacto está en `SKILL_canon.md` (idéntico al `SKILL.md` de la
> conversación).  v1.1.3 P2-10: cualquier referencia externa al SKILL
> debe apuntar a este archivo para evitar ambigüedad de versión.

## Convenciones

| Estado | Significado |
|---|---|
| `current` | Implementado y verificado por tests reproducibles |
| `specification` | Definido normativamente; no necesariamente automatizado |
| `planned` | Diseñado para fase posterior; requiere implementación |
| `future` | Visión o fase empresarial posterior |
| `experimental` | Existe pero no es estable/canónico |
| `deprecated` | Permitido por compatibilidad, no recomendado |

## Matriz de capacidades (v1.1.9)

| Capacidad | Estado | Evidencia |
|---|---|---|
| Parser `.cortex → AST` | `current` | `parse_cortex()`, suite de tests completa |
| Writer `AST → .cortex` determinista | `current` | `write_cortex()`, roundtrip textual OK |
| AST canónico con hashes estructurales | `current` | `CortexDocument`, `Entry.hash` SHA-256 |
| `$0` obligatorio y primero | `current` | Parser levanta `E001`/`E002` |
| Glosario mínimo local autocontenido | `current` | `build_minimal_glossary()` con sigilos canónicos + tipos + micro |
| Validación sintáctica (sigilos/tipos/duplicados) | `current` | `validate()` |
| Validación cognitiva (separación de niveles) | `current` (1.1.1) | `validate_level_policy()`, `E023`/`E024`/`E026`/`E029` |
| `validate()` acepta `kind` explícito | `current` (1.1.1) | `validate(doc, strict, kind)` — fix H-RA-01 |
| `--kind` gobierna validación real | `current` (1.1.1) | `verify --kind` y `doctor --kind` aplican reglas |
| Separación Nivel 1 con SES/LNG | `current` (1.1.1) | `LIVE_SESSION_SIGILS` incluido en `LIVE_STATE_SIGILS` — fix H-RA-02 |
| Dominio `survive` validado | `current` (1.1.0) | `ALLOWED_SURVIVE`, `E025` |
| `attrs-pos` con arity check | `current` (1.1.0) | `E027_ATTRS_POS_ARITY` |
| `attrs-pos` prohíbe `|` en valores | `current` (1.1.1) | `serialize_attrs_pos()` rechaza pipes — fix H-RA-05 |
| Detección de secretos en claro (no-bypassable) | `current` (1.1.3) | `E031_SECRET_NOT_BYPASSABLE` con `bypassable=False` — fix P0-2 |
| Sigilos críticos incompletos bloqueados | `current` (1.1.3) | `E032_CRITICAL_SIGIL_INCOMPLETE` con `bypassable=False` — fix P0-3 |
| FCS/OBJ `done` no cuenta como activo | `current` (1.1.3) | `active_status={current,blocked}` — fix P0-4 |
| Invariantes de gobernanza non-bypassable | `current` (1.1.4) | E023/E024/E026/E029 `bypassable=False`; --force no puede degradar cerebro operativo — fix P0-1 |
| Forensic quarantine marker | `current` (1.1.4) | `STAT:forensic_quarantine` con `--unsafe-allow-secret-forensics` — fix P0-3 |
| $0 section integrity (no operational memory) | `current` (1.1.5) | `E033_ZERO_SECTION_MEMORY_ENTRY` non-bypassable; $0 solo metadato estructural — fix P0-1 |
| FCS/OBJ bajo $0 no satisfacen Nivel 2 | `current` (1.1.5) | Level policy excluye $0 al iterar — fix P0-2 |
| recover entry-first visible en HCORTEX | `current` (1.1.5) | Payload movido a $1: RECOVERED CONTENT — fix P0-3 |
| add --section $0 rechaza memoria operativa | `current` (1.1.5) | `add_entry()` bloquea con E033 — fix P0-4 |
| HCORTEX advierte sobre $0 con entradas operativas | `current` (1.1.5) | `render_hcortex_read()` muestra WARNING — fix P1-5 |
| Critical field emptiness blocked (E034) | `current` (1.1.6) | `E034_CRITICAL_REQUIRED_FIELD_EMPTY` non-bypassable; "", "   ", null = empty — fix P0-1 |
| FCS/OBJ vacíos no satisfacen Nivel 2 | `current` (1.1.6) | Level policy verifica `what`/`goal` no vacíos — fix P0-3 |
| recover mueve ops de $0 existente | `current` (1.1.6) | recover siempre separa ops de $0 — fix P1-4 |
| recover retorna non-zero si no conforme | `current` (1.1.6) | recover valida post-procesamiento — fix P1-5 |
| Null semántico bloqueado (None + "null" string) | `current` (1.1.7) | `_is_field_empty()` trata "null" como vacío; parser convierte bare null a None — fix P0-1/P0-3 |
| recover aísla contenido en sección dedicada | `current` (1.1.7) | recover usa $99 si $1 ya existe — fix P1-4 |
| recover marca estado vivo recuperado con RSK | `current` (1.1.7) | W011_RECOVERED_LIVE_STATE para FCS/OBJ/WRK/STP/NXT — fix P1-5 |
| recover repara $0 existente incompleto | `current` (1.1.9) | W012 + auto-declaración de sigilos observados ausentes; verify strict pasa |
| --embed-aud-rsk traza reparación de $0 incompleto | `current` (1.1.9) | AUD:recovery + RSK:incomplete_glossary_repaired + RSK:auto_declared_* |
| Demo sentinels valida E034 explícito | `current` (1.1.9) | nombres sanitizados y grep de E034, no solo rc != 0 |
| recover elige sección libre real | `current` (1.1.8) | escanea hasta encontrar la primera sección libre sin techo artificial — Fix 1 |
| --embed-aud-rsk embebe RSK para live state | `current` (1.1.8) | RSK:recovered_live_* en artefacto — Fix 2 |
| AUD describe evento real | `current` (1.1.8) | glossary_reconstruction vs live_state_recovered_from_zero — Fix 3 |
| E034 cubre null-like sentinels | `current` (1.1.8) | none, nil, undefined, n/a, tbd, ???, -, -- — Fix 4 |
| HCORTEX-READ (vista humana) | `current` (1.1.3) | Perfil como primera línea real — fix P1-5 |
| HCORTEX-READ con `--layout priority` | `current` (1.1.1) | Orden global P0→P5 — fix H-RA-03 |
| HCORTEX-AUDIT con `Mode: AUDIT` | `current` (1.1.3) | `audit_mode_str` refleja modo real — fix P1-6 |
| HCORTEX-AUDIT con `source` uniforme | `current` (1.1.3) | `source:` visible en cuerpo/bloque — fix P1-7 |
| HCORTEX-EDIT (reversible) | `current` | `render_hcortex_edit()` + `parse_hcortex_edit()` |
| Roundtrip estructural HCORTEX-EDIT | `current` | `verify --roundtrip hcortex-edit` |
| Roundtrip con pipes/unicode/bloques | `current` (1.1.1) | `_split_markdown_row()` respeta `\|`; attrs-pos prohíbe `\|` |
| CRUD de entradas (add/update/delete/move) | `current` | `crud/mutations.py` |
| CRUD bloquea sigilos desconocidos | `current` (1.1.1) | `add_entry()` levanta `UnknownSigilError` — fix H-RA-06 |
| Validación post-mutación (add/update/delete/move) | `current` (1.1.2) | `post_mutation_gate()` compartido — Fix 4 |
| Protección P0 (FCS/OBJ/CNST blocking) | `current` | `is_protected_entry()`, `E009` |
| CRUD de glosario (sigilos) | `current` | `glossary add/update/delete` |
| CRUD de micro-tokens | `current` | `micro add/update/delete` |
| Escritura atómica con backup | `current` | `atomic_write_cortex()` con `.tmp`/`.bak` |
| Modo `--strict` (warnings → errors) | `current` (1.1.0) | `validate(strict=True)` |
| Recuperación de artefactos legacy | `current with known limits` (1.1.3) | `recover_cortex()` con `--embed-aud-rsk`; soporta archivos sin `$0` que empiezan con entradas (v1.1.3 P0-1); límite: no cubre glosarios legacy con columnas no canónicas no mapeadas |
| Operaciones de diagrama | `current` (1.1.1) | `cortex diagram list/extract/validate`; extract verbatim — fix H-RA-04 |
| Diff estructural/semántico | `current` | `cortex diff --profile structural|semantic` |
| Diff governance (cambios reales) | `current` (1.1.2) | `_extract_governance_changes()` detecta cambios en entradas de gobernanza — Fix 5 |
| Aliases CLI canónicos | `current` (1.1.0) | `decode`/`encode`/`patch_add`/`patch_update`/`patch_remove` |
| `decode <file>` sin `--mode` | `current` (1.1.3) | default a `readable` — fix P2-8 |
| JSON output para automatización | `current` (1.1.2) | `--json` global produce JSON real en new/render/diff/verify — Fix 7 |
| Inferencia de `document_kind` | `current` (1.1.0) | `infer_document_kind()` |
| Compilación desde HCORTEX-READ | `current` (rechazado) | `E010_HCORTEX_READ_NOT_COMPILABLE` |
| `cortex new brain/skill/package/generic` | `current` | `templates/` |
| Benchmark reproducible | `planned` | `BENCHMARK.md` define metodología; script formal pendiente |
| Parser throughput `measured` | `hypothesis` (1.1.1) | Reclasificado desde `measured` — fix H-RA-07 |
| Demo portátil sin rutas absolutas | `current` (1.1.2) | `scripts/cortex_demo_v1_1_2.sh` — Fix 1 |
| Modo `migrate` (legacy → canónico) | `planned` | `recover` cubre el 80%; falta `--from legacy-skill-alpha` |
| MCP server | `future` | No implementado |
| Runtime de maduración (promote/decay) | `future` | No implementado |
| Promoción/decaimiento automático | `future` | No implementado |

## Cambios por versión

- **1.1.9** (esta versión): cierre de recuperación enterprise para $0 incompleto.
  Fix 1 (recover repara $0 existente pero incompleto),
  Fix 2 (--embed-aud-rsk traza reparación con AUD/RSK),
  Fix 3 (sección libre sin techo artificial),
  Fix 4 (demo sentinels valida E034 explícito).
  Suite ampliada: 217 → 222 tests.
- **1.1.8**: cierre de bordes de recovery y null-like.
  Fix 1 (recover elige sección libre real),
  Fix 2 (--embed-aud-rsk embebe RSK para live state),
  Fix 3 (AUD describe evento real),
  Fix 4 (E034 cubre none, nil, undefined, n/a, tbd, ???, -, --).
  Suite ampliada: 196 → 217 tests.
- **1.1.7**: cierre de brecha de null semántico.
  P0-1 ("null" string tratado como vacío),
  P0-2 (OBJ.success:null, CNST.rule:null, etc. bloqueados),
  P0-3 (update --set field=null serializa None, no "null"),
  P1-4 (recover aísla contenido en sección dedicada $99 si $1 existe),
  P1-5 (recover añade RSK W011 para estado vivo recuperado).
  Suite ampliada: 183 → 196 tests.
- **1.1.6**: cierre de frontera de vacuidad semántica.
  P0-1 (E034_CRITICAL_REQUIRED_FIELD_EMPTY non-bypassable),
  P0-2 ("", "   ", null = campo faltante),
  P0-3 (FCS/OBJ vacíos no satisfacen Nivel 2),
  P1-4 (recover mueve ops de $0 existente),
  P1-5 (recover retorna non-zero si no conforme),
  P1-6 (benchmark de recovery visible + semántica no vacía).
  Suite ampliada: 169 → 183 tests.
- **1.1.5**: cierre de brecha estructural $0.
  P0-1 (E033 prohíbe memoria operativa en $0),
  P0-2 (FCS/OBJ bajo $0 no satisfacen Nivel 2),
  P0-3 (recover entry-first mueve payload a $1: RECOVERED CONTENT),
  P0-4 (add --section $0 rechaza memoria operativa),
  P1-5 (HCORTEX advierte sobre $0 con entradas operativas),
  P1-6 (BENCHMARK mide recovery por visibilidad HCORTEX).
  Suite ampliada: 158 → 169 tests.
- **1.1.4**: hardening de gobernanza operativa.
  P0-1 (E024 non-bypassable → --force no puede degradar cerebro),
  P0-2 (invariantes E023/E024/E026/E029 todas bypassable=False),
  P0-3 (--unsafe-allow-secret-forensics marca STAT:forensic_quarantine),
  P1-4 (pytest como dev dependency),
  P1-5 (demo v1.1.4),
  P1-6 (RSK general en recover incluso para sigilos canónicos).
  Suite ampliada: 147 → 158 tests.
- **1.1.3**: hardening de bordes de gobernanza.
  P0-1 (recover reconstruye $0 para archivos entry-first),
  P0-2 (E031_SECRET_NOT_BYPASSABLE no-bypassable con --force),
  P0-3 (E032_CRITICAL_SIGIL_INCOMPLETE bloquea sigilos críticos incompletos),
  P0-4 (FCS/OBJ status:done no cuenta como activo),
  P1-5 (Perfil como primera línea real de HCORTEX),
  P1-6 (render --mode audit declara Mode:AUDIT),
  P1-7 (source visible en cuerpo/bloque),
  P2-8 (decode sin --mode funciona),
  P2-9 (claim recovery rebajado a "current with known limits"),
  P2-10 (canon SKILL sincronizado via SKILL_canon.md).
  Suite ampliada: 124 → 147 tests.
- **1.1.2**: hardening post-tercera-revisión.
  Fix 1 (demo portable), Fix 2 (recover --embed-aud-rsk declara AUD/RSK),
  Fix 3 (test recover+embed+verify --strict), Fix 4 (post-mutation gate
  para update/delete/move), Fix 5 (diff governance detecta cambios reales),
  Fix 6 (BENCHMARK.md sin rutas absolutas), Fix 7 (--json produce JSON real).
- **1.1.1**: hardening quirúrgico post-re-auditoría.
  Fix H-RA-01 (`--kind` gobierna validación), H-RA-02 (SES/LNG en skill),
  H-RA-03 (`--layout priority|section`), H-RA-04 (diagram extract verbatim),
  H-RA-05 (attrs-pos prohíbe `|`), H-RA-06 (CRUD bloquea sigilos desconocidos),
  H-RA-07 (BENCHMARK reclasificado), H-RA-08 (versión SKILL consistente),
  H-RA-09 (artefactos en tarball), M-RA-02 (diff governance JSON rc),
  M-RA-03 (`recover --embed-aud-rsk`), M-RA-04 (metadata canónica en recover).
- **1.1.0**: hardening del validador (cognitive governance),
  HCORTEX canónico con perfiles y P0→P5, fix de pipes en tablas,
  `cortex recover` para legacy, `cortex diagram`, aliases `decode/encode/patch_*`,
  `--strict`, `--kind`, `--profile`, `LICENSE`, `STATUS.md`, `BENCHMARK.md`,
  `CHANGELOG.md`.
- **1.0.0**: implementación inicial — parser, AST, writer, HCORTEX-READ/EDIT,
  compile, CRUD, atomic write, 15 criterios de aceptación cubiertos.

## Limitaciones declaradas

- El parser es determinista pero **tolerante** con líneas no parseables
  (las registra como `E017_UNPARSED_LINE` warning, salvo patrones de
  entrada con llaves desbalanceadas que se marcan como error `E005`).
- `expand_micro()` es conservadora: solo expande tokens delimitados.
  Nunca expande dentro de palabras ni dentro de `bloque`.
- No se implementan `decode/encode` como operaciones separadas del
  codec: son aliases de `render`/`compile` respectivamente, alineados
  con el contrato planificado del SKILL §22.2.
- El escaneo de secretos es heurístico y conservador; puede tener falsos
  positivos en prosa y falsos negativos en formatos no cubiertos.
