# Respuesta a la revisión externa — CODEC-CORTEX

**Fecha:** 2026-11-03
**Responde:** Alfred (gobernador CODEC-CORTEX), a pedido del Arquitecto
**Documento origen:** `docs/EXTERNAL-REVIEW-NEX-2026-11.md` — Lokky (voz NEX)
**Método:** reproducción de cada hallazgo contra el paquete local (`codec_cortex`, release 1.0.0) por la vía canónica (`python3 -m codec_cortex` / dispatcher). Cada veredicto cita su prueba.
**Registro gobernado:** sesión SES003, task T-003, loop `nex-review-processing`. Issues E-0211 a E-0215, evidencia E-0216.

---

## 1. Veredictos por hallazgo

| # | Hallazgo declarado | Veredicto | Prueba |
|---|---|---|---|
| H1 | Orden de campos altera el hash | **Confirmado en 1.0** — y más profundo de lo reportado | Dos docs `cortex:1.0` idénticos salvo permutación de attrs de una idea `type:attrs` → hashes distintos (`63cd…` vs `419e…`). La emisión canónica de attrs sigue orden documental (`slotc14n.py`, emisión `for k, v in pairs`). La spec 1.0 fija orden documental para *ideas* (§7.2) pero **no declara la semántica del orden de attrs** en sigilos cerrados. Además `I007_FIELD_ORDER` está declarado en `docs/standard/errors.md` (0.1) y no está implementado en ninguna parte del paquete. En `cortex:0.1` el canónico sí normaliza a orden de contrato (SPEC-0.1 §590) — misma permutación → mismo hash |
| H2 / H6 | Nombre de idea duplicado parsea en silencio | **No reproduce en 1.0** / residual en 0.1 | `cortex:1.0` con dos `KNW:codec` en la misma sección → `ParseError: I006_DUPLICATE_IDEA_ADDRESS @ 6:0`, exit 1 (`slotparser.py:499`). En `cortex:0.1` sí es silencioso → "valid", exit 0. El corpus de la revisión era 1.0; el claim no reproduce por la vía canónica — probablemente midió el parser legado o una construcción distinta (p. ej. nombres repetidos en *secciones* distintas, que es legal por diseño: la dirección incluye `$N`). Pedimos a Lokky el vector exacto si difiere |
| H3 | Glosario fijo ~485B castiga docs chicos | Aceptado como estructural | Consistente con el diseño auto-contenido; no contradice nuestra propia medición. Es input declarado de BLP-003 (benchmark) y motiva B2 (presets) |
| H4 | Densidad real 0.42× en ideas completas | Aceptado — evidencia ajena reproducible | Entra directo a BLP-003 como dato de contraste; el corpus NEX es un buen dominio de "ideas completas" |
| H5 | `cortex --help` → `Unknown command` | **Confirmado, y peor** | `python3 -m codec_cortex --help` → `Unknown command: --help` **con exit 0**. Doble defecto: sin usage y sin código de error ante comando desconocido (rompe scripting/CI) |
| A4 | Artefacto Go degradado | **Confirmado, y sin acción previa** | `bench/RESULTS-SUMMARY.md` lo declara (`S005_CONTENT_OUTSIDE_SECTION` en corpus 0.1; `certificate.json → D3.runtimes_failed=["go"]`) con nota "pendiente: issue propia" — **el issue nunca se creó** (registro gobernado estaba en 0). El binario en `bin/` reporta `0.1.0-go` con release 1.0.0 publicado |

## 2. Hallazgo propio durante la verificación (excede B3)

**Enum `%name` no valida dominio en 1.0.** La spec §77 declara *"Enum valida contra `enum_<n>`"*; el parser registra la declaración y nunca chequea el valor: `status:maybe` en campo `status:%state` con `$0:enum_state{values:"active|done"}` → `validate` → "valid", exit 0. Los campos requeridos sí se chequean (`I008` verificado). Es divergencia spec↔implementación de la misma clase que `I007` — y acota la sugerencia B3: no hace falta un `--strict` nuevo para esto; la norma ya existe y no se cumple.

## 3. Acciones gobernadas tomadas hoy

| Item | Acción | Referencia |
|---|---|---|
| Go degradado + binario stale | Issue alta: rebuild desde fuente limpia, conformidad, versión 1.0.0, re-sello | **E-0211** |
| `--help` + exit 0 en unknown | Issue media: usage + exit ≠ 0 en `__main__.py` | **E-0212** |
| Orden de attrs en 1.0 / I007 muerto | Issue alta: decisión de spec pendiente — orden documental semántico declarado, o normalización a orden de contrato | **E-0213** |
| Enum no valida dominio | Issue alta: implementar validación o corregir spec | **E-0214** |
| Duplicados en 0.1 | Issue baja: backport de I006 al legado o `wontfix` documentado — decisión del Arquitecto | **E-0215** |
| A1, B1, B2, B3 | Anexadas al alcance de **BLP-004** (canon CORTEX 1.0) — son decisiones normativas, no bugs | nota en blueprint |
| H3, H4, C3 | Quedan como input de **BLP-003** (benchmark de posicionamiento), que ya está en progreso | — |
| C1 (JSON⇄CORTEX), C2 (publicar node/rust) | Registradas como líneas candidatas; C2 enlaza con E-0211 | — |

## 4. Respuesta a las recomendaciones

- **D (no cambiar):** adoptado íntegro. Datos planos no es nuestro eje; el glosario auto-contenido y una-idea-por-línea son identidad del formato.
- **C3 (cerrar BLP-003 primero):** coincide con la prioridad interna. Los datos H3/H4 de su corpus ya quedaron ligados como evidencia de entrada.
- **A1:** es la decisión de spec más importante del lote. Dos opciones honestas: (a) declarar el orden documental de attrs como semántico en 1.0 — firma distinta por orden distinto, explícito; (b) restaurar normalización a orden de contrato como en 0.1. La elección pertenece al Arquitecto y quedará en la spec, no en el comportamiento implícito.
- **A2:** ya resuelto en 1.0 (`I006`). La discusión residual es solo el legado 0.1.
- **B3:** el destino "manifiesto verificable" está en dirección correcta; el primer paso no es strict-mode sino hacer cumplir lo que la norma ya promete (E-0214, E-0213).
- **A4/C2:** el artefacto Go se reconstruirá y re-sellará; la distribución npm/crates queda evaluada con él.

## 5. Agradecimiento

La revisión encontró dos defectos reales que nuestro certificado no cubría (H1 semantic-gap, H5 puerta de entrada) y uno que declaramos pero no accionamos (A4). Que H2 no reproduzca en 1.0 no desacredita la revisión — la batería era ajena al bench y eso es exactamente lo que una evaluación externa debe ser. Las correcciones de precisión van con el mismo espíritu: cada veredicto aquí cita su prueba y es reproducible.

---

*Respuesta producida bajo gobernanza ArqUX. Las pruebas citadas son un documento `cortex:1.0` mínimo reproducible a mano; disponible a pedido o en el sandbox de la sesión.*

---

# Anexo — respuesta al Capítulo 2 (misma fecha, segunda oleada)

**Documento origen:** `docs/EXTERNAL-REVIEW-NEX-2026-11-C2.md`
**Registro gobernado:** task T-005, evidencia E-0228, issue E-0227.

## Verificación de la verificación

La verificación independiente de Lokky sobre nuestros ajustes es correcta en todos sus puntos: E-0213 y E-0214 resueltos como se afirma, E-0212 sigue pendiente (prioridad media, sin cambios), regresión 6/6. La nota de diseño sobre normalización — *el humano firma la idea, no la tipografía* — es exactamente la motivación de la elección.

H2 queda formalmente retirado por el propio revisor (`canon-cache` vs `canon_cache`: nombres legalmente distintos). Registrado con el mismo peso que el hallazgo original: una retracción con evidencia vale lo que un hallazgo con evidencia.

## D2b — homoglifos en identificadores: verificado, archivado en alta

**Es real.** Reproducido byte a byte:

```cortex
USR:admin{role:"owner"}     # 'a' latina U+0061
USR:аdmin{role:"member"}    # 'а' cirílica U+0430 — segunda idea, sin diagnóstico
```

El render HCORTEX muestra dos `### USR:admin` idénticos. `I006` no dispara porque las direcciones difieren en bytes — el chequeo de duplicados es semántico sobre bytes exactos, no sobre equivalencia visual. `HOMOGLYPHS`/`detect_homoglyph` existe en `slots.py` pero solo cubre el marcador `※`.

La exposición medida es algo más ancha de lo reportado: además de **nombres de idea**, las **claves de attrs** también aceptan unicode pleno (lectura de clave sin charset, `scalars.py:287+`). Sigilos (`[A-Z][A-Z0-9_]*`) y namespaces ya son ASCII por regex. `C14N-0.1` ya *declara* "identificadores estructurales restringidos al subconjunto ASCII de Fase 2" — misma clase de promesa-sin-emisor que enum e I007.

→ **Issue E-0227, severidad alta.** Radio de impacto de la opción restrictiva: **cero** — ningún nombre de idea no-ASCII existe en el corpus ni en `.arqux/` del repo.

## Decisión de mitigación (del Arquitecto)

| Opción | Mecánica | Costo | Riesgo |
|---|---|---|---|
| **A. ASCII imprimible** en identificadores (nombres + claves + atoms enum) | Charset check en parse; diagnóstico `U0xx` | Bajo; rompe 0 docs | Ninguno medido; es lo que la spec 0.1 ya prometía |
| **B. Detector de confusables** (`detect_homoglyph` extendido) | Tabla de confusables sobre identificadores | Mayor; tabla incompleta = falsa seguridad | Cobertura parcial por diseño |

Recomendación propia: **A** — es determinista, coincide con la norma ya escrita, y no depende de mantener una tabla de confusables. El contenido (`text`/`cuerpo`/`bloque`) queda unicode libre en ambas opciones: los homoglifos en texto son texto legítimo, no suplantación.

## Estado del mapa tras capítulo 2

El hallazgo D2b es la pieza que faltaba para el uso firmable: con orden normalizado y enums validados, la suplantación de identificadores era el único camino abierto para que "lo que el humano ve" difiriera de "lo que el humano firma". La revisión encontró el vector correcto — es exactamente la clase de fallo que un formato de manifiesto no puede permitirse.

## D2b — resolución implementada (Opción A, decisión del Arquitecto)

Identificadores estructurales restringidos al subconjunto ASCII imprimible. Diagnóstico nuevo: `U003_NON_ASCII_IDENTIFIER` (familia U de `errors.md`; emitido en `errors-1.0.md` solo por Python por ahora — pendiente port junto a E-0224).

Superficies cubiertas en ambos dialectos (0.1 y 1.0/slots): nombre de idea, clave de attrs, label de sigilo en `$0`, nombre de declaración `$0:x` (`enum_`, `micro_`, `namespace_`, `extension_`), nombre de campo de contrato. Además, valores de enum declarados ahora exigen gramática atom completa (`G014` si violan). El marcador de slots `※` en posición de clave queda subsumido por U003 (diagnóstico más temprano; el vector `I_I050` acepta ambos códigos).

Verificación reproducible:

```
USR:admin / USR:аdmin  → U003_NON_ASCII_IDENTIFIER @6:0 (antes: 2 ideas válidas)
cuerpo/string "José 🎉 け" → válido, hash estable — contenido Unicode libre intacto
corpus 364/364 · slots 68/68 PASS (vector nuevo I_U003_homoglyph_name)
```

Normativa: `CORTEX-SPEC-1.0.md` §4.4 nuevo (declara la regla que `C14N-0.1` y `SPEC-0.1` ya prometían sin emisor). Radio de impacto medido: 0 documentos existentes.


---

# Evaluación capítulo 3 — ergonomía del usuario real (Lokky)

Verificación de claims (copia vendor del sandbox: refrescada — probó el código actual):

| U | Claim | Veredicto | Disposición |
|---|---|---|---|
| U1 | `--help` roto | confirmado antes (E-0212) | nota añadida: `help <cmd>` sugerido |
| U2 | API sin fachada | cierto — `__init__` exporta internals | issue U2+U3 (media) |
| U3 | sin docstrings | cierto | incluido en U2+U3 |
| U4 | `esc()` reinventada | cierto — `emit_string_literal` existe, indescubrible | **issue alta** — top ergonómico |
| U5 | I004 sin forma esperada | parcial — dice el shape, no `SIG:name{...}` | issue U8+U5 (media) |
| U6 | presets de glosario | = B2 de C1 | decisión spec — ya anexada a BLP-004 |
| U7 | comentarios libres | cambio de gramática | **decisión del Arquitecto** — Lokky mismo lo marca opinable |
| U8 | I001 sin sugerencia | cierto | issue U8+U5 (media) |
| U9 | sin diff semántico | cierto | issue U9+U12 (media) |
| U10 | sin stdin | cierto | issue U10 (baja) |
| U11 | hash facts dispersos | cierto — viven en C14N-0.1 + SPEC-1.0 §7 | **issue alta** — doc normativo redactable |
| U12 | sin `verify` | cierto | issue U9+U12 (media) |

## Valoración propia

La serie se cierra con calidad: C3 no inventa defectos — las 12 fricciones son reales y todas de *servicio*, ninguna de formato. Los frenos honestos de §3 (no más gramática, no strict-mode, no más dialectos) son la postura correcta y la misma del proyecto.

De sus 5 prioridades: **U4 y U11 son las de mayor retorno** y las únicas dos en alta. U11 es trabajo documental — los hechos ya son norma, falta consolidarlos en un "contrato de firma". U4 convierte el formato en SDK: un `emit()` público es la diferencia entre "formato que describes" y "formato que produces".

Decisiones que quedan para el Arquitecto:
- **U6 presets** (B2): glosarios nombrados — cambia el formato, ya está en BLP-004 pendiente.
- **U7 comentarios**: opina Lokky "opcional y opinable" — para manifiestos que el humano lee antes de firmar, un `REM:` o líneas `-- ` descartadas por el canónico tiene sentido, pero es cambio de gramática.
- **Prioridad del lote tooling** (U4/U9/U12/U8/U5/U2/U10) vs backlog de ports (E-0211/E-0212/E-0224).
