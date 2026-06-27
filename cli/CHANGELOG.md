# CHANGELOG — codec-cortex

Todos los cambios notables de este proyecto se documentan en este archivo.
El formato se adhiere a [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
y el versionado a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.9] — 2026-06-27

### Resumen

Cierre de recuperación enterprise para `$0` existente pero incompleto y
endurecimiento de demo: `recover` ahora auto-declara sigilos usados pero
ausentes en `$0`, embebe AUD/RSK para esa reparación y los demos verifican
`E034` explícitamente sin falsos positivos por nombres de archivo.

### Fix 1: recover repara `$0` existente pero incompleto

- **Problema:** si `$0` existía pero omitía sigilos usados por el payload
  (`KNW`, `RSK`, etc.), `recover` no lo completaba y el artefacto seguía
  fallando con `E003_UNKNOWN_SIGIL`.
- **Fix:** `_repair_incomplete_glossary()` auto-declara sigilos observados
  ausentes y asegura tipos canónicos en el `$0` local.
- **Tests:** `test_recover_repairs_existing_incomplete_glossary`,
  `test_recover_cli_repairs_incomplete_glossary_and_returns_zero`.

### Fix 2: AUD/RSK para reparación de glosario incompleto

- **Problema:** la reparación de `$0` incompleto no dejaba traza embebida
  equivalente a los flujos de reconstrucción.
- **Fix:** `--embed-aud-rsk` agrega `AUD:recovery` con
  `event:"incomplete_glossary_repair"` y `RSK:incomplete_glossary_repaired`
  más riesgos por sigilo auto-declarado.
- **Tests:** `test_recover_embed_aud_rsk_for_incomplete_glossary_repair`,
  `test_recover_incomplete_glossary_content_visible_in_hcortex`.

### Fix 3: sección libre sin techo artificial

- **Problema:** la estrategia anterior escaneaba rangos acotados.
- **Fix:** `_first_free_recovery_section_id()` busca indefinidamente la
  primera sección libre positiva y evita contaminar secciones existentes.
- **Test:** `test_recover_uses_free_section_even_when_many_sections_exist`.

### Fix 4: demo v1.1.9 sin falso positivo de sentinel

- **Problema:** el demo v1.1.8 podía construir nombres de archivo inválidos
  con `n/a` y aprobar por `rc != 0` sin verificar `E034`.
- **Fix:** `scripts/cortex_demo_v1_1_9.sh` sanitiza nombres y exige que la
  salida contenga `E034_CRITICAL_REQUIRED_FIELD_EMPTY`.

### Tests

- Suite ampliada: 217 → 222 tests (5 nuevos de v1.1.9).

## [1.1.8] — 2026-06-27

### Resumen

Cierre de bordes de recovery y null-like: recovery nunca contamina
secciones existentes, AUD describe el evento real, RSK se embebe para
estado vivo recuperado, y E034 cubre todos los null-like sentinels
comunes (none, nil, undefined, n/a, tbd, ???, -, --).

### Fix 1: Recovery elige sección libre real

- **Problema:** recover usaba $99 si $1 existía, pero si $99 también
  existía, contaminaba esa sección.
- **Fix:** recover ahora escanea $1, $2, ..., $99, $100, ... hasta
  encontrar la primera sección verdaderamente libre.
- **Tests:** `test_recover_finds_free_section_when_1_and_99_exist`,
  `test_recover_never_contaminates_existing_section`.

### Fix 2: --embed-aud-rsk embebe RSK para W011_RECOVERED_LIVE_STATE

- **Problema:** recover emitía W011_RECOVERED_LIVE_STATE como
  diagnóstico, pero `--embed-aud-rsk` no insertaba RSK equivalentes
  en el artefacto.
- **Fix:** `_embed_recovery_trace()` ahora inserta `RSK:recovered_live_*`
  para cada sigilo de estado vivo movido desde $0.
- **Tests:** `test_embed_aud_rsk_inserts_rsk_for_moved_live_state`.

### Fix 3: AUD describe el evento real

- **Problema:** AUD:recovery siempre decía
  `event:"glossary_reconstruction"` incluso cuando el $0 no fue
  reconstruido (solo se movieron entradas).
- **Fix:** AUD ahora describe el evento real: `glossary_reconstruction`
  si se reconstruyó $0, `live_state_recovered_from_zero` si se movió
  estado vivo, o ambos combinados.
- **Tests:** `test_aud_describes_real_event_not_always_glossary_reconstruction`,
  `test_aud_describes_glossary_reconstruction_when_it_happened`.

### Fix 4: E034 cubre null-like sentinels

- **Problema:** `none`, `nil`, `undefined`, `n/a`, `tbd`, `???`, `-`
  pasaban como valores válidos en campos críticos.
- **Fix:** `_is_field_empty()` ahora detecta todos estos sentinels
  (case-insensitive). El parser de attrs y el CLI `--set` también
  convierten `none`/`nil`/`undefined` a Python None.
- **Tests:** 10 tests parametrizados para cada sentinel + test de
  valores reales no bloqueados.

### Tests

- Suite ampliada: 196 → 217 tests (21 nuevos de v1.1.8).

## [1.1.7] — 2026-06-27

### Resumen

Cierre de la brecha de null semántico: el literal `null` (como Python None
o como string "null") ya no puede usarse como valor válido en campos
críticos requeridos. Recovery ahora aísla contenido recuperado en sección
dedicada y marca estado vivo recuperado con RSK.

### P0 — Cierre obligatorio

#### P0-1: String "null" tratado como vacío en campos críticos

- **Problema:** `_is_field_empty()` solo detectaba None, "" y "   ".
  El string "null" (que el parser de attrs y el CLI `--set` producían
  para el literal `null`) pasaba como valor válido.
- **Fix:** `_is_field_empty()` ahora trata "null" (case-insensitive,
  con strip) como vacío.

#### P0-2: OBJ.success:null, CNST.rule:null, RSK.mitigation:null, AUD.evidence:null bloqueados

- Cubierto por P0-1: todos los campos requeridos de sigilos críticos
  ahora rechazan null (None o "null") vía E034.
- **Tests:** `test_obj_success_null_blocked`, `test_cnst_rule_null_blocked`,
  `test_rsk_mitigation_null_blocked`, `test_aud_evidence_null_blocked`.

#### P0-3: update --set field=null serializa None, no "null"

- **Problema:** `_parse_set_pairs()` dejaba "null" como string, que se
  serializaba como `rule:"null"` y pasaba validación.
- **Fix:** `_parse_set_pairs()` ahora convierte "null"/"None" a Python None.
  `parse_attrs_body()` también convierte bare `null` a None.
- **Tests:** `test_update_set_null_converts_to_none`,
  `test_update_set_null_blocked_by_e034`.

### P1 — Recovery y trazabilidad

#### P1-4: recover crea sección dedicada RECOVERED CONTENT aunque $1 exista

- **Problema:** recover usaba `get_or_create_section("$1")`, que si $1
  ya existía con título "IDENTITY", le añadía entradas recuperadas
  rompiendo trazabilidad semántica.
- **Fix:** recover ahora verifica si $1 existe; si existe, usa $99
  para RECOVERED CONTENT.
- **Tests:** `test_recover_uses_dedicated_section_when_1_exists`.

#### P1-5: recover añade RSK cuando se mueve FCS/OBJ/WRK/STP/NXT desde $0

- **Fix:** recover emite `W011_RECOVERED_LIVE_STATE` cuando se mueven
  sigilos de estado vivo desde $0, advirtiendo que se activó estado
  recuperado y debe verificarse antes de confiar en él.
- **Tests:** `test_recover_adds_rsk_for_moved_live_state`,
  `test_recover_no_rsk_for_non_live_state`.

### Tests

- Suite ampliada: 183 → 196 tests (13 nuevos de v1.1.7).

## [1.1.6] — 2026-06-27

### Resumen

Cierre de la frontera de vacuidad semántica: un brain formalmente válido
pero semánticamente vacío (FCS:primary{what:""}) ya no pasa verificación.
Recovery ahora retorna non-zero si no puede producir un artefacto conforme.

### P0 — Cierre obligatorio

#### P0-1: E034_CRITICAL_REQUIRED_FIELD_EMPTY

- **Problema:** FCS:primary{what:""} pasaba `verify --strict` porque el
  campo `what` existía (no era missing), solo estaba vacío. El brain era
  formalmente válido pero semánticamente vacío.
- **Fix:** Nuevo código `E034` (`bypassable=False`) que trata `""`,
  `"   "` (whitespace-only) y `null` como campo faltante en sigilos
  críticos. Se distingue de E032 (campo ausente) — E034 es campo presente
  pero vacío.
- **Tests:** `test_e034_empty_string_in_critical_field`,
  `test_e034_whitespace_only_in_critical_field`,
  `test_e034_null_in_critical_field`, `test_e034_non_bypassable`,
  `test_e034_not_fired_for_non_empty_value`.

#### P0-2: "", "   ", null tratados como campo faltante

- Helper `_is_field_empty()` que detecta None, "" y strings whitespace-only.
- Aplicado a todos los sigilos críticos con `REQUIRED_FIELDS`.

#### P0-3: FCS/OBJ vacíos no satisfacen Nivel 2

- **Problema:** Un brain con FCS:primary{what:"", status:"current"} pasaba
  E024 porque el status era activo, aunque el foco estuviera vacío.
- **Fix:** La validación de Nivel 2 ahora verifica que `what` (para FCS)
  y `goal` (para OBJ) no estén vacíos antes de contar la entrada como activa.
- **Tests:** `test_empty_fcs_does_not_satisfy_level2`,
  `test_empty_obj_does_not_satisfy_level2`,
  `test_non_empty_fcs_obj_satisfies_level2`.

### P1 — Recovery y benchmark

#### P1-4: recover mueve memoria operativa fuera de $0 aunque $0 ya exista

- **Problema:** recover solo movía entradas de $0 cuando reconstruía el
  glosario. Si el $0 ya existía pero tenía entradas operativas mezcladas,
  recover no las separaba.
- **Fix:** recover ahora SIEMPRE mueve entradas operativas de $0 a
  `$1: RECOVERED CONTENT`, sin importar si $0 fue reconstruido o ya existía.
- **Tests:** `test_recover_moves_ops_from_existing_zero`.

#### P1-5: recover retorna non-zero si no puede producir artefacto conforme

- **Problema:** recover siempre retornaba 0, incluso si el artefacto
  recuperado tenía errores non-bypassable que recovery no podía fixar.
- **Fix:** recover ahora valida el artefacto recuperado post-procesamiento
  y retorna `1` si hay errores. El archivo se escribe de todas formas
  (para inspección), pero el rc señala que no es conforme.
- **Tests:** `test_recover_returns_zero_for_conformant_input`,
  `test_recover_returns_zero_for_repairable_entry_first`.

#### P1-6: Benchmark de recovery visible + semántica no vacía

- Nuevas métricas en BENCHMARK.md: `Recovery semantic non-emptiness`,
  `Recovery conformant exit code`, `Critical field emptiness blocked`.
- **Tests:** `test_benchmark_has_recovery_semantic_non_emptiness`,
  `test_benchmark_has_e034_metric`.

### Tests

- Suite ampliada: 169 → 183 tests (14 nuevos de v1.1.6).
- Nuevo código de error: `E034_CRITICAL_REQUIRED_FIELD_EMPTY`.

## [1.1.5] — 2026-06-27

### Resumen

Cierre de la brecha estructural `$0`: prohibición de memoria operativa
en la sección de metadatos estructurales. Esta era la brecha central
que permitía memoria invisible — el corazón de CODEC-CORTEX.

### P0 — Cierre obligatorio

#### P0-1: Prohibir entradas operativas en $0 (E033_ZERO_SECTION_MEMORY_ENTRY)

- **Problema:** El CLI permitía entradas operativas (FCS, OBJ, KNW, etc.)
  dentro de `$0`. Como HCORTEX omite `$0` por diseño, esas entradas eran
  invisibles en la vista auditable.
- **Fix:** Nuevo código `E033_ZERO_SECTION_MEMORY_ENTRY` (`bypassable=False`).
  Solo se permiten sigilos de declaración de glosario (GSIG/GTYP/GMIC/GCON)
  como entradas en `$0`.
- **Tests:** `test_verify_rejects_memory_entries_in_zero_section`,
  `test_verify_rejects_memory_entries_in_zero_section_cli`.

#### P0-2: FCS/OBJ bajo $0 no satisfacen Nivel 2

- **Problema:** Un brain con FCS/OBJ solo en `$0` pasaba `verify --strict`
  porque `iter_entries()` incluía `$0` al buscar FCS/OBJ activos.
- **Fix:** Las validaciones de Nivel 1, 2 y 3 ahora excluyen `$0` al iterar.
  Solo las entradas fuera de `$0` cuentan como estado operativo.
- **Tests:** `test_brain_fcs_obj_under_zero_do_not_satisfy_level2`.

#### P0-3: recover entry-first mueve payload a $1: RECOVERED CONTENT

- **Problema:** `recover` de archivos entry-first dejaba las entradas
  originales dentro de `$0`, haciéndolas invisibles a HCORTEX.
- **Fix:** `_reconstruct_glossary()` ahora inserta `$1: RECOVERED CONTENT`
  antes de las entradas originales cuando el archivo empieza con entradas
  (no con sección). El payload recuperado queda visible en HCORTEX.
- **Tests:** `test_recover_entry_first_moves_payload_to_section_1`,
  `test_recover_entry_first_verify_strict_passes`,
  `test_recover_entry_first_hcortex_shows_payload`.

#### P0-4: cortex add --section $0 rechaza entradas operativas

- **Problema:** `cortex add --section $0 --sigil NXT` permitía esconder
  estado operativo en `$0`.
- **Fix:** `add_entry()` rechaza añadir sigilos operativos a `$0` con
  `E033_ZERO_SECTION_MEMORY_ENTRY`. Solo GSIG/GTYP/GMIC/GCON están permitidos.
- **Tests:** `test_add_to_zero_rejects_operational_entry`,
  `test_add_to_zero_allows_glossary_sigil`.

### P1 — Auditoría y benchmark

#### P1-5: HCORTEX advierte sobre entradas en $0

- **Fix:** `render_hcortex_read()` ahora incluye un bloque `⚠ WARNING`
  al inicio del output si `$0` contiene entradas operativas, listando
  las entradas ocultas y sugiriendo `cortex verify --strict` para corregir.
- **Tests:** `test_hcortex_warns_about_zero_section_entries`,
  `test_hcortex_no_warning_for_clean_brain`.

#### P1-6: BENCHMARK.md mide recovery por visibilidad HCORTEX

- **Fix:** Añadida métrica `Recovery visibility (HCORTEX)` que requiere
  que las entradas recuperadas sean visibles en `render --mode audit
  --profile full`, no solo que `verify --strict` pase.
- **Tests:** `test_benchmark_recovery_visibility_claim`.

### Tests

- Suite ampliada: 158 → 169 tests (11 nuevos de v1.1.5).
- Nuevo código de error: `E033_ZERO_SECTION_MEMORY_ENTRY`.

## [1.1.4] — 2026-06-27

### Resumen

Hardening de bordes de gobernanza operativa. Cierra los 4 problemas
detectados en la quinta verificación. La brecha central era que `--force`
podía degradar el cerebro operativo por debajo del mínimo CODEC-CORTEX.

### P0 — Cierre obligatorio

#### P0-1: E024_LEVEL2_MISSING_FOCUS es non-bypassable

- **Problema:** `cortex delete brain.cortex FCS:primary --force` persistía
  un brain sin FCS activo. Luego `verify --strict` fallaba con E024, pero
  el archivo ya estaba escrito.
- **Fix:** E024_LEVEL2_MISSING_FOCUS ahora tiene `bypassable=False`. Ni
  `--force` ni `--no-validate-write` pueden sobrepasarlo. El
  `post_mutation_gate` bloquea la escritura antes de tocar el archivo.
- **También se aplica a:** E023_LEVEL1_LIVE_STATE, E026_BLOCKING_NOT_P0,
  E029_LEVEL3_LIVE_STATE (todas las invariantes de gobernanza cognitiva
  son ahora `bypassable=False`).
- **Tests:** `test_force_delete_fcs_blocked`, `test_force_delete_obj_blocked`,
  `test_force_update_fcs_to_done_blocked`, `test_non_governance_force_still_works`.

#### P0-2: --force no puede eliminar P0 operativo

- Cubierto por P0-1: las invariantes E023/E024/E026/E029 son non-bypassable,
  por lo que `--force` no puede eliminar FCS, OBJ, CNST:blocking ni STP
  si eso rompe las invariantes del cerebro operativo.

#### P0-3: --unsafe-allow-secret-forensics marca non_conformant

- **Problema:** El flag forense escribía un .cortex con secreto y respondía
  `ok:true` sin marcar el artefacto como no conforme.
- **Fix:** Cuando se usa `--unsafe-allow-secret-forensics`, se añade una
  entrada `STAT:forensic_quarantine` con `conformity:"non_conformant_forensic_artifact"`
  y `status:"deprecated"`. El JSON de respuesta incluye un `warning` que
  aclara que el artefacto NO debe usarse como memoria operativa.
- **Tests:** `test_unsafe_forensics_marks_non_conformant`,
  `test_unsafe_forensics_verify_still_fails`.

### P1 — Contrato CLI/documentación

#### P1-4: pytest como dependencia dev

- **Problema:** `pip install -e .` no instalaba pytest; las instrucciones
  de test no eran reproducibles en venv limpia.
- **Fix:** Añadido `[project.optional-dependencies] dev = ["pytest>=7.0"]`
  en pyproject.toml. Instrucciones actualizadas: `pip install -e ".[dev]"`.
- **Tests:** `test_pytest_dev_dependency_declared`.

#### P1-5: Demo v1.1.4

- **Problema:** No existía demo v1.1.3; el empaquetado seguía siendo
  `cortex_demo_v1_1_2.sh`.
- **Fix:** Creado `scripts/cortex_demo_v1_1_4.sh` que prueba los 6 fixes
  de v1.1.4 de forma portable y reproducible.
- **Tests:** `test_demo_v1_1_4_exists`, `test_demo_v1_1_4_runs_successfully`.

#### P1-6: RSK general cuando recover reconstruye $0

- **Problema:** recover solo añadía RSK para sigilos no canónicos
  reconstruidos. Si todos los sigilos eran canónicos, no quedaba RSK
  que marcara el riesgo de la reconstrucción.
- **Fix:** recover ahora añade siempre `RSK:reconstructed_glossary` cuando
  el $0 fue reconstruido, incluso si todos los sigilos son canónicos.
  El RSK declara que la metadata canónica puede no coincidir con la
  intención original.
- **Tests:** `test_recover_adds_general_rsk_for_canonical_sigils`,
  `test_recover_general_rsk_has_correct_fields`.

### Tests

- Suite ampliada: 147 → 158 tests (11 nuevos de v1.1.4).
- Las invariantes de gobernanza (E023/E024/E026/E029) son ahora
  `bypassable=False`, alineadas con E031 (secretos) y E032 (sigilos
  críticos incompletos).

## [1.1.3] — 2026-06-27

### Resumen

Hardening de bordes de gobernanza post-cuarta revisión. Cierra los 10
problemas detectados en `CODEC_CORTEX_VERIFICACION_v1_1_2_HCORTEX.md`:
4 P0 (críticos), 3 P1 (auditoría/salida), 3 P2 (CLI/documentación).

### P0 — Cierre obligatorio

#### P0-1: recover reconstruye $0 para archivos que empiezan con entradas

- **Problema:** `recover` no detectaba "glosario vacío con entradas
  observables" como equivalente a missing-glossary. Un archivo que
  empezaba con `IDN:package{...}` se parseaba con un `$0` implícito
  vacío, y `recover` no reconstruía los sigilos.
- **Fix:** `recover_cortex()` ahora verifica post-parse si
  `glossary.sigils` está vacío mientras hay entradas observables, y
  dispara la reconstrucción en ese caso.
- **Tests:** `test_recover_entry_first_file_without_glossary`,
  `test_recover_entry_first_file_cli_verify_strict`.

#### P0-2: E031_SECRET_NOT_BYPASSABLE no es bypassable con --force

- **Problema:** `--force` permitía persistir secretos en claro, lo que
  contradice el SKILL §16.1 (`.cortex` MUST NOT almacenar secretos).
- **Fix:**
  - Nuevo código `E031_SECRET_NOT_BYPASSABLE` (reemplaza `E028` para
    secret scanning) con campo `bypassable=False`.
  - `post_mutation_gate()` y `atomic_write_cortex()` respetan
    `bypassable=False`: ni `--force` ni `--no-validate-write` los sobrepasan.
  - Nuevo flag `--unsafe-allow-secret-forensics` para bypass forense
    explícito de secretos (no de critical-sigil completeness).
- **Tests:** `test_secret_not_bypassable_with_force`,
  `test_secret_bypassable_with_unsafe_forensics_flag`,
  `test_secret_finding_tagged_non_bypassable`.

#### P0-3: CRUD bloquea sigilos críticos incompletos por defecto

- **Problema:** `W001_MISSING_FIELDS` era warning, permitiendo persistir
  `OBJ:partial{goal:"partial"}` sin los campos requeridos.
- **Fix:** Nuevo código `E032_CRITICAL_SIGIL_INCOMPLETE` (error,
  `bypassable=False`) para sigilos críticos con campos faltantes.
- **Tests:** `test_critical_sigil_incomplete_blocked_by_default`,
  `test_critical_sigil_incomplete_not_bypassable_with_force`,
  `test_critical_sigil_complete_passes`.

#### P0-4: FCS/OBJ status:done no cuenta como activo

- **Problema:** Un brain con FCS y OBJ en `status:"done"` pasaba
  `verify --strict --kind brain`. `done` es estado cerrado, no activo.
- **Fix:** `active_status` cambiado de `{current, blocked, done}` a
  `{current, blocked}`. Mensaje de error aclara que `done` es closed state.
- **Tests:** `test_fcs_obj_done_not_active`, `test_fcs_obj_current_passes`,
  `test_fcs_obj_blocked_passes`.

### P1 — Auditoría y salida

#### P1-5: Perfil como primera línea real de HCORTEX

- **Problema:** HCORTEX-READ empezaba con `<!-- cortex-render: ... -->`,
  no con `Perfil: CORTEX-<LEVEL>` como exige el SKILL §9.3.
- **Fix:** `Perfil: CORTEX-<LEVEL>` ahora es la primera línea; el
  comentario `cortex-render` va en la segunda.
- `edit_parser.py` actualizado para detectar HCORTEX-READ/EDIT en las
  primeras 5 líneas (no solo la primera).
- **Tests:** `test_perfil_is_first_line_of_hcortex_read`,
  `test_perfil_first_line_all_profiles`.

#### P1-6: render --mode audit declara Mode: AUDIT

- **Problema:** `render --mode audit` declaraba `Mode: READABLE`
  internamente.
- **Fix:** `audit_mode_str` ahora refleja el modo real (`AUDIT` si
  audit_mode, sino el modo del usuario).
- **Tests:** `test_audit_mode_declares_audit`,
  `test_readable_mode_declares_readable`.

#### P1-7: source visible en cuerpo/bloque

- **Problema:** En AUDIT mode, `source` solo aparecía como columna en
  tablas attrs; cuerpo y bloque solo tenían comentarios HTML.
- **Fix:** `render_entry()` ahora añade una línea visible
  `source: \`<SIGIL>:<name>\`` antes de bloques cuerpo/bloque/relación
  en AUDIT mode.
- **Tests:** `test_source_visible_for_cuerpo_in_audit`,
  `test_source_visible_for_bloque_in_audit`,
  `test_source_not_visible_in_readable_mode`.

### P2 — Contrato CLI/documental

#### P2-8: cortex decode <file> con default usable

- **Problema:** `cortex decode <file>` fallaba sin `--mode`, aunque el
  SKILL §22.2 planea `decode <file> [--format ...]`.
- **Fix:** `--mode` ahora es opcional con default `readable`. `decode`
  y `render` funcionan sin `--mode`.
- **Tests:** `test_decode_without_mode_defaults_to_readable`,
  `test_render_without_mode_defaults_to_readable`.

#### P2-9: Claim de recovery legacy rebajado

- **Problema:** STATUS.md declaraba recovery legacy como `current`
  sin salvedad, pero fallaba en casos adversariales.
- **Fix:** Cambiado a `current with known limits` con descripción de
  qué cubre y qué no.
- **Tests:** `test_status_md_recovery_claim_has_limits`.

#### P2-10: Sincronizar canon SKILL externo e interno

- **Problema:** Ambigüedad sobre la versión del SKILL (v1.1.0 vs
  v1.2.0) entre la conversación y el tarball.
- **Fix:** STATUS.md ahora declara explícitamente que
  `SKILL_canon.md` es el canon exacto (`v1.2.0-enterprise-candidate`)
  y que cualquier referencia externa debe apuntar a ese archivo.
- **Tests:** `test_skill_canon_present_and_versioned`,
  `test_status_md_declares_skill_version`.

### Tests

- Suite ampliada: 124 → 147 tests (23 nuevos de v1.1.3).
- 2 nuevos códigos de error: `E031_SECRET_NOT_BYPASSABLE`,
  `E032_CRITICAL_SIGIL_INCOMPLETE`.

## [1.1.2] — 2026-06-27

### Resumen

Hardening quirúrgico post-tercera-revisión. Cierra los 7 problemas
detectados por el usuario en la verificación de v1.1.1.

### Fixed — Demo portable con exit 1 real (Fix 1)

- `scripts/cortex_demo_v1_1_2.sh` no usa rutas absolutas del entorno.
  Localiza `cortex` desde `PATH` o vía `PYTHONPATH` con detección
  automática de `src/` relativo al script.
- El demo ahora **termina con `exit 1` real** si cualquier paso de
  verificación falla (antes imprimía "ALL FIXED" incluso con fallos).
- Helpers `expect_rc_zero` / `expect_rc_nonzero` cuentan fallos y
  propagan el rc al shell.

### Fixed — recover --embed-aud-rsk declara AUD/RSK en $0 (Fix 2)

- `_embed_recovery_trace()` ahora asegura que `AUD` y `RSK` estén
  declarados en `$0` antes de insertar las entradas.  Si faltan (típico
  cuando el glosario fue reconstruido), se auto-declara con metadata
  canónica de `brain_sigils()` y se emite un diagnóstico
  `I003_SIGIL_AUTO_DECLARED`.
- Antes (v1.1.1): insertar `AUD:recovery` sin declarar `AUD` en `$0`
  hacía que `verify --strict` fallara con `E003_UNKNOWN_SIGIL`.
- Ahora: el flujo `recover --embed-aud-rsk` + `verify --strict` pasa
  limpiamente.

### Added — Test recover + embed + verify --strict (Fix 3)

- `test_recover_embed_then_verify_strict` (API interna)
- `test_recover_embed_then_verify_strict_cli` (CLI end-to-end)
- Ambos verifican que el artefacto recuperado con AUD/RSK embebidos
  pasa `verify --strict` sin errores.

### Added — Validación post-mutación para update/delete/move (Fix 4)

- `cortex.cli.commands.post_mutation_gate()` helper compartido que
  valida el AST después de una mutación y bloquea la escritura si hay
  errores (a menos que `--force`).
- `update`, `delete`, `move` ahora usan el mismo gate que `add`.
- Nuevos flags CLI para los tres comandos: `--no-validate-write`,
  `--strict-write`.
- Tests nuevos:
  - `test_cli_update_blocked_by_validation`
  - `test_cli_update_force_bypasses_gate`
  - `test_cli_delete_blocked_by_validation`
  - `test_cli_move_post_mutation_validation`
  - `test_internal_post_mutation_gate_helper`

### Fixed — diff --profile governance detecta cambios reales (Fix 5)

- Antes (v1.1.1): comparaba solo `findings` de `validate_level_policy`.
  Dos archivos válidos con un `CNST` cambiado → rc=0 (falso negativo).
- Ahora: `_extract_governance_changes()` filtra los diffs de
  `compare_ast()` para quedarse solo con los que afectan sigilos de
  gobernanza (`FCS`, `OBJ`, `WRK`, `STP`, `NXT`, `CNST`, `AXM`, `!`,
  `RSK`, `AUD`, `CLAIM`, `LIM`, `KNW`).
- Retorna non-zero si hay cualquier cambio en entradas de gobernanza,
  además de si hay findings.
- Tests nuevos:
  - `test_diff_governance_detects_cnst_change`
  - `test_diff_governance_equal_files_returns_zero`
  - `test_diff_governance_ignores_non_governance_changes`

### Fixed — BENCHMARK.md sin rutas absolutas ni conteo hardcoded (Fix 6)

- Eliminadas todas las rutas `/home/z/...` del archivo.
- Eliminada la referencia hardcodeada a `88/88 tests` (que quedó
  desactualizada cuando la suite creció a 110+).
- Ahora el archivo declara explícitamente que el conteo no se hardcodea
  y apunta al comando `python -m pytest src/tests/ -q` para obtener el
  número actual.
- Tests nuevos:
  - `test_benchmark_no_absolute_paths`
  - `test_benchmark_roundtrip_count_matches_suite` (redefinido para
    verificar que no hay conteo hardcoded)

### Fixed — --json produce JSON real en new y render (Fix 7)

- `cortex --json new ...` ahora emite JSON parseable con `{ok, path,
  bytes, kind}` (antes era texto plano).
- `cortex --json render ...` ahora emite JSON con `{ok, input, mode,
  markdown}` cuando no hay `--out`, o `{ok, out, bytes}` cuando hay
  `--out`.
- README actualizado: aclara que `--json` es un flag global que va
  **antes** del subcomando (`cortex --json new ...`).
- Tests nuevos:
  - `test_cli_new_json_produces_valid_json`
  - `test_cli_render_json_produces_valid_json`
  - `test_cli_render_json_to_file`

### Tests

- Suite ampliada: 110 → 124 tests (14 nuevos de v1.1.2).

## [1.1.1] — 2026-06-26

### Resumen

Hardening quirúrgico post-re-auditoría. Cierra las brechas H-RA-01 a
H-RA-09 y M-RA-01 a M-RA-05 detectadas en
`CODEC_CORTEX_REAUDIT_v1_1_0_HCORTEX.md`.

### Fixed — Gobierno cognitivo (H-RA-01, M-RA-01)

- `validate()` ahora acepta parámetro `kind: Optional[DocumentKind]` y lo
  pasa a `validate_level_policy()`.
- `verify --kind <kind>` y `doctor --kind <kind>` ahora afectan la
  validación real (no solo display). Antes: `verify --kind package` no
  aplicaba reglas de Nivel 3; ahora sí.
- `is_valid()` también acepta `kind`.
- Tests CLI end-to-end nuevos:
  `test_cli_verify_kind_package_overrides_idn_agent`,
  `test_cli_verify_kind_skill_overrides_filename_or_idn`,
  `test_cli_verify_kind_generic_disables_level_policy`,
  `test_cli_doctor_kind_skill_overrides_filename`.

### Fixed — Separación Nivel 1 con SES/LNG (H-RA-02)

- `LIVE_STATE_SIGILS` ahora incluye `SES` y `LNG` además de
  `FCS/OBJ/WRK/STP/NXT`.
- Nuevas constantes: `LIVE_WORKING_SIGILS`, `LIVE_SESSION_SIGILS`,
  `SKILL_FORBIDDEN_LIVE_SIGILS`.
- `SES`/`LNG` marcados como `nature=example` o `status=specification`
  se permiten en Nivel 1 (forma de contrato/ejemplo).
- Tests nuevos:
  `test_g2_strict_skill_with_live_ses_fails`,
  `test_g2_strict_skill_with_live_lng_fails`,
  `test_g2_strict_skill_with_historical_ses_example_passes`.

### Added — HCORTEX --layout priority|section (H-RA-03)

- `render_hcortex_read()` acepta `layout` parameter (`priority` o `section`).
- Auto-selección: MIN/RECOVERY/AUDIT → `priority` (global P0→P5);
  WORK/FULL/READABLE → `section` (preserva secciones).
- `_render_priority_layout()`: agrupa entradas por P-level (P0 primero,
  P5 último) independientemente del orden de secciones.
- CLI: `cortex render --layout priority|section`.
- Tests nuevos:
  `test_hcortex_layout_priority_orders_p0_before_p2`,
  `test_hcortex_layout_priority_default_for_min`,
  `test_hcortex_layout_section_preserves_section_order`.

### Fixed — Diagram extract verbatim (H-RA-04)

- `cortex diagram extract --out` ahora escribe exactamente los bytes
  del bloque (sin añadir newline final).
- `cortex diagram extract` (stdout) también escribe exactamente los
  bytes; flag `--print-newline` para añadir newline en consola.
- Test nuevo: `test_g7_diagram_extract_out_preserves_exact_bytes`.

### Fixed — attrs-pos prohíbe `|` en valores (H-RA-05)

- `serialize_attrs_pos()` levanta `InvalidValueError` si algún valor
  contiene `|`. El usuario debe usar `attrs` en su lugar.
- `parse_attrs_pos_body()` documenta explícitamente que `|` es el
  delimiter y no puede aparecer en valores (no se implementa
  quote-aware splitting a propósito — máxima compresión, contrato estable).
- Tests nuevos:
  `test_attrs_pos_writer_rejects_pipe_in_value`,
  `test_attrs_pos_with_pipe_in_value_does_not_roundtrip_silently`.

### Fixed — CRUD bloquea sigilos desconocidos (H-RA-06)

- `add_entry()` ahora levanta `UnknownSigilError` por defecto si el
  sigilo no está en `$0`.
- Nuevo parámetro `allow_unknown_sigil=True` para recovery/debug.
- CLI: `cortex add --allow-unknown-sigil`, `--no-validate-write`,
  `--strict-write`.
- Por defecto, `cortex add` valida antes de persistir; si la mutación
  produce errores, se rechaza la escritura (a menos que `--force`).
- Tests nuevos:
  `test_cli_add_rejects_unknown_sigil_by_default`,
  `test_cli_add_allows_unknown_sigil_with_flag`,
  `test_add_entry_internal_blocks_unknown_sigil`.

### Fixed — BENCHMARK.md reclasificación (H-RA-07)

- "Parser throughput" reclasificado de `measured` a `hypothesis`
  (era una estimación, no un benchmark formal).
- "Roundtrip structural fidelity" actualizado de 61/61 a 88/88 tests.
- Tests nuevos:
  `test_benchmark_throughput_not_measured`,
  `test_benchmark_roundtrip_count_matches_suite`.

### Fixed — Versión SKILL consistente (H-RA-08)

- `STATUS.md` ahora declara explícitamente `SKILL.md v1.2.0-enterprise-candidate`.
- `SKILL_canon.md` incluido en el tarball del proyecto.
- Test nuevo: `test_declared_skill_version_matches_reference_file`.

### Fixed — diff governance JSON rc (M-RA-02)

- `cortex diff --profile governance --format json` ahora retorna
  non-zero si hay findings (antes siempre retornaba 0).
- Test nuevo: `test_cli_diff_governance_json_returns_nonzero_on_findings`.

### Added — recover --embed-aud-rsk (M-RA-03)

- `recover_cortex(embed_aud_rsk=True)` inserta entradas `AUD` y `RSK`
  en el `.cortex` recuperado para que el artefacto mismo cargue la
  traza de recuperación.
- CLI: `cortex recover --embed-aud-rsk`.
- Tests nuevos:
  `test_recover_embed_aud_rsk_inserts_entries`,
  `test_recover_embed_aud_rsk_cli`.

### Fixed — recover metadata canónica (M-RA-04)

- `_reconstruct_glossary()` ahora usa prioridad brain > skill > package
  para sigilos compartidos (IDN, DOM, etc.). Antes: `IDN:agent` podía
  heredar "Package identity"; ahora hereda "Actor or memory identity".

### Added — Artefactos en el tarball (H-RA-09)

- `scripts/cortex_demo_v1_1.sh` incluido en `scripts/` dentro del tarball.
- `SKILL_canon.md` incluido en la raíz del proyecto.
- `AUDIT_BASE.md` (la auditoría original) incluido como trazabilidad.

### Tests

- Suite ampliada: 88 → 110 tests (22 nuevos tests de re-auditoría).
- Todos los tests CLI end-to-end usan `sys.exit(rc)` para propagar
  correctamente el código de retorno al shell.

## [1.1.0] — 2026-06-25

### Resumen

Hardening del validador con gobierno cognitivo, HCORTEX canónico con
perfiles y P0→P5, fix de pipes en tablas Markdown, modo `recover` para
artefactos legacy, operaciones de diagrama, aliases CLI canónicos y
gobernanza de madurez (`STATUS.md`, `BENCHMARK.md`, `LICENSE`).

Cierra las brechas de auditoría: H-01, H-02, H-03, H-04, H-05, H-06,
B-001, B-002, B-003, B-004, B-006, B-007, B-008, B-009, B-010, M-01,
M-02, M-03, M-05, M-06, L-01, L-03.

### Added — Gobierno cognitivo (Fase 1)

- `cortex/core/document_kind.py`: `DocumentKind`, `infer_document_kind()`,
  `validate_level_policy()`.
- Detección de tipo de documento (skill/brain/package/generic) por IDN,
  filename o signatura de sigilos.
- Validación de separación de niveles: Nivel 1 sin estado vivo, Nivel 2
  requiere FCS+OBJ activos, Nivel 3 sin WRK vivo.
- Dominio `survive` validado: `{min, recovery, work, full}`.
- `CNST:blocking` obliga `survive:min` (P0).
- `attrs-pos` con arity incorrecto genera `E027_ATTRS_POS_ARITY` (no
  más pérdida silenciosa de campos sobrantes).
- Escaneo de secretos en claro (api_key, password, token, AWS, private
  key, URLs con credenciales) → `E028_SECRET_IN_CLEAR`.
- Nuevos códigos de error: `E023`–`E030`.
- `validate(strict=True)`: promueve warnings a errors para `verify --strict`.

### Added — HCORTEX canónico (Fase 2)

- `cortex/hcortex/profiles.py`: `Profile`, `PROFILES`
  (MIN/RECOVERY/WORK/FULL), `resolve_profile()`, `classify_entry()`,
  `filter_by_profile()`, `sort_by_plevel()`.
- Clasificador P0→P5 basado en sigilo + `survive` + `severity`.
- `render_hcortex_read(profile, mode)`: soporta modos READABLE, AUDIT,
  RECOVERY, FULL.
- Primera línea canónica: `Perfil: CORTEX-<LEVEL>` en HCORTEX-READ.
- Orden P0→P5 en la salida.
- Modo AUDIT agrega columna `source` con `<SIGIL>:<name>` en tablas.
- Declaración de omisiones por presupuesto al final del render.

### Fixed — Roundtrip con valores complejos (Fase 2)

- `_split_markdown_row()`: split de filas Markdown que respeta `\|`.
  Antes: `what:"A | B"` se rompía a `A \`. Ahora preserva el pipe.
- Aplicado a `_parse_markdown_table` y `_parse_attrs_table`.

### Added — Recuperación legacy (Fase 3)

- `cortex/hcortex/recovery.py`: `recover_cortex()`, `strip_preamble()`,
  `normalise_legacy_type_name()`.
- Tolerancia a preámbulos SPDX, front-matter Markdown, HTML comments,
  headings antes de `$0`.
- Alias `contenido → cuerpo`, `Expansion → Type`, `body → cuerpo`,
  `code → bloque`, etc.
- Reconstrucción de `$0` mínimo cuando el archivo no lo tiene, con
  diagnósticos `RSK` por cada sigilo reconstruido.
- Comando CLI `cortex recover <file> --out <file>`.

### Added — Operación CLI canónica (Fase 4)

- Aliases: `decode` (= `render`), `encode` (= `compile`),
  `patch_add` (= `add`), `patch_update` (= `update`),
  `patch_remove` (= `delete`).
- `cortex diagram list/extract/validate` para entradas DIAG.
- `cortex doctor --strict --kind brain|skill|package|generic`.
- `cortex verify --strict --kind <kind> --roundtrip hcortex-edit|cortex`.
- `cortex diff --profile structural|semantic|governance`.
- `cortex render --mode readable|audit|recovery|full --profile min|recovery|work|full`.
- `--json` global normalizado (stasheado en `args._json_mode`).

### Removed

- `--with-cortex-out` fantasma en `cortex new` (audit gap B-005).

### Added — Gobernanza de madurez (Fase 5)

- `LICENSE` (MIT) físico en el repo.
- `STATUS.md` con matriz de capacidades y clasificación de madurez.
- `BENCHMARK.md` con métricas `measured`/`target` y metodología
  reproducible.
- `CHANGELOG.md` (este archivo).
- `README.md` reescrito sin overclaim: "implementa un subconjunto
  funcional del codec CODEC-CORTEX".

### Tests

- Suite de tests ampliada: 61 → 61 + nuevos tests de gates (G1–G8) en
  `test_audit_gates.py`.

## [1.0.0] — 2026-06-24

### Resumen

Implementación inicial del CLI `cortex` conforme a la especificación
algorítmica modular y al canon `SKILL.md` v1.2.0-enterprise-candidate.

### Added

- Arquitectura modular: `core/`, `glossary/`, `hcortex/`, `crud/`,
  `templates/`, `cli/`.
- Parser `.cortex → AST` (lexer + parser determinista, sin LLM).
- Writer canónico `AST → .cortex` determinista.
- Validador sintáctico (sigilos desconocidos, tipos, duplicados).
- HCORTEX-READ (vista humana) y HCORTEX-EDIT (vista editable reversible).
- Compilador HCORTEX-EDIT → `.cortex`.
- Roundtrip estructural `.cortex → HCORTEX-EDIT → .cortex`.
- CRUD completo (add/update/delete/move + glossary + micro).
- Escritura atómica con backup `.bak`.
- 15 comandos CLI: new, render, compile, verify, get, list, add, update,
  delete, move, glossary, micro, doctor, diff, format.
- 61 tests (15 criterios de aceptación + CRUD + errores + fixtures).
- Templates brain/skill/package/generic.
