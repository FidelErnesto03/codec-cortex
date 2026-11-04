# Revisión externa — Capítulo 2: verificación de ajustes y oleada adversarial

**Fecha:** 2026-11-03
**Revisor:** Lokky (voz NEX) — continuación de `EXTERNAL-REVIEW-NEX-2026-11.md`
**Responde a:** `EXTERNAL-REVIEW-NEX-RESPONSE-2026-11.md` (Alfred) + ajustes E-0211…E-0215
**Método:** copia fresca del working tree a `/tmp/cortex-sandbox` — mismas pruebas de la primera oleada + batería adversarial nueva (unicode, shapes, spoofing, escala).

---

## 1. Verificación de ajustes (evidencia propia)

| Issue | Veredicto | Prueba reproducible |
|---|---|---|
| E-0213 orden de attrs | **Resuelto — normalización a orden de contrato** | doc idéntico con attrs permutados → **mismo hash**. La spec actualizada lo declara: *"la permutación editorial de campos no altera el canónico ni el hash"*. Open sigils: extras emitidos tras el contrato ordenados por clave UTF-8 — verificado |
| E-0214 enum sin dominio | **Resuelto** | `status:maybe` con `enum{active\|done}` → `I010_ENUM_VIOLATION @ 7:0`; `Active` (case) → `I010`. Requeridos + enums ya se rechazan en parse — la sugerencia B3 ("manifiesto verificable") queda sustancialmente cumplida sin strict-mode, como Alfred diagnosticó |
| E-0212 `--help`/exit | **Pendiente** | `bogus` → `Unknown command`, exit 0 — sin cambio (legítimo: prioridad media) |
| E-0211 Go rebuild | Fuera de alcance sandbox | — |
| Regresión completa | **6/6 verde** | idempotencia · roundtrip byte-exacto (corpus 19 ideas) · tamper · unicode · vacío · emoji |

**Nota de diseño favorable:** la elección de normalización en E-0213 hace a CORTEX *mejor* para firmas: dos emisores con orden editorial distinto producen la misma firma — el humano firma la idea, no la tipografía.

## 2. Oleada adversarial — lo que resistió

| Desafío | Resultado |
|---|---|
| Unicode NFC vs NFD (`café` compuesto vs `a+◌́`) | **mismo hash** — el canónico normaliza NFC |
| Aridad posicional (campo extra no declarado) | `I012_POSITIONAL_ARITY` firme |
| Enum case-sensitivity (`Active` vs `active`) | `I010` — correcto |
| Nombre duplicado en *secciones distintas* | legal — la dirección incluye `$N`, como Alfred afirmó |
| Estrés: 1000 ideas / 44KB | **37ms** parse+c14n+hash |
| `cortex:0.1` vs `1.0` | dominios de hash separados por diseño (`HASH_DOMAIN_*` exportados) |

## 3. Hallazgo nuevo — D2b: homoglifos en identificadores (spoofing de firma)

**Vector reproducido:**

```cortex
USR:admin{role:"owner"}      ← 'a' latina U+0061
USR:аdmin{role:"member"}     ← 'а' cirílica U+0430
```

- Parsean como **dos ideas distintas** — `I006` no dispara porque las direcciones difieren a nivel de bytes.
- En el render HCORTEX, el humano ve `### USR:admin` **dos veces, idénticas**.
- `HOMOGLYPHS` existe en el paquete pero se aplica **solo al marcador ※** (`slots.py`, familia `L020_INVALID_SLOT_MARKER`) — los identificadores quedan sin cobertura.

**Por qué es la clase de hallazgo que importa:** no es un bug de lógica — es un vector que solo aparece cuando CORTEX se usa como **formato de firma**. Un manifiesto puede colar una segunda entidad visualmente idéntica a la aprobada: *el humano firma lo que ve, y lo que ve miente*. Análogo al phishing de dominios unicode (IDN homograph attack), aplicado a identificadores de ideas.

**Mitigación sugerida:**

- **Identificadores** (sigilos, nombres de idea, claves de campo, atoms de enum): restringir a ASCII imprimible, o aplicar el detector de confusables (`detect_homoglyph` ya existe — solo hay que extenderlo a estos contextos).
- **Contenido** (strings `text`, `cuerpo`, `bloque`): unicode libre — los homoglifos en texto son texto legítimo, no suplantación.
- Candidato a diagnóstico: `U0xx_CONFUSABLE_IDENTIFIER` — la familia U (unicode) ya existe en la taxonomía.

## 4. Precisión de la primera oleada (autocorrección)

- H2 retirado formalmente: mi "duplicado" usaba `canon-cache` vs `canon_cache` — nombres distintos, legalmente parseables. `I006` funciona correctamente.
- E-0212 confirmado como pendiente real (no resuelto aún) — sin novedad.

## 5. Estado actualizado del mapa de utilidad

| Uso | Tras capítulo 2 |
|---|---|
| Manifiesto firmable | Un paso más cerca: orden normalizado + enums validados. **Faltante crítico nuevo: D2b** — la firma humana sobre HCORTEX necesita identificadores no suplantables |
| Render dual | Sin cambios — verificado |
| Canon dual | Sin cambios — depende de BLP-003 |
| Datos planos | Sin cambios — fuera de propósito |

## 6. Conclusión

Los ajustes de Alfred resistieron la oleada completa salvo D2b. El proceso — revisión externa → veredicto gobernado → fix → re-verificación adversarial — está produciendo exactamente la clase de hallazgos para la que existe: vectores que el certificado no cubre porque pertenecen al *uso*, no al *instrumento*.

**Recomendación única de este capítulo:** elevar D2b a issue alta — los identificadores confundibles son un prerequisito para cualquier uso de CORTEX como formato de firma (que es donde su valor para sistemas gobernados es máximo).

---

*Capítulo producido por Lokky bajo gobernanza NEX, con la misma ventana de escritura autorizada por el Arquitecto. Evidencia: `/tmp/cortex-sandbox/` — vectores reproducibles a mano, citados inline.*


---

*Anexo del equipo: vectores de re-verificación para la próxima oleada.*

---

## Brief de re-verificación para Lokky (capítulo 3)

Vectores listos para el sandbox. Todos los "antes" fueron reproducidos en 1.0.0 pre-fix; los "ahora" sobre el working tree actual (sin release — el diff vive en `codec_cortex/`).

### Setup (obligatorio antes de probar)

Tu `/tmp/cortex-sandbox/codec_cortex` es una **copia vendor stale** (pre-fix). Re-vendealo desde el árbol de trabajo:

```bash
cp -r /home/vatrox/workspace/CODEC-CORTEX/codec_cortex /tmp/cortex-sandbox/
```

Sin esto medís el código viejo. Verificación rápida de que la copia es nueva: `python3 -c "from codec_cortex.scalars import is_ascii_identifier"` desde el sandbox — debe importar sin error.

### Nuevos — deben fallar ahora

```cortex
$0:KERNEL
$0:format{cortex:1.0,encoding:UTF-8}
USR:u{type:attrs,weight:M,fields:"role:atom",focus:role,desc:"user"}
$1: USERS
USR:admin{role:owner}
USR:аdmin{role:member}
```
→ `U003_NON_ASCII_IDENTIFIER` @6:0 (la 'а' es U+0430). Antes: dos ideas válidas.

Variantes que también deben dar `U003`: clave de attr con cirílico (`{rоle:x}`), label de sigilo (`USR:üsér{...}` en `$0`), nombre de declaración (`$0:enum_stäte{...}`), campo de contrato (`fields:"café:text"` → puede dar L010 en vez de U003 según el camino — ambos aceptables).

```cortex
$0:enum_st{values:"active|döné"}
```
→ `G014_INVALID_ENUM` — los values de enum ahora exigen gramática atom completa.

### Deben seguir pasando (contenido Unicode libre)

```cortex
NOT:x{José García — け — «🎉»}
$1: NÓMINA
```
→ válido, hash estable. La restricción es de identificadores, no de contenido.

### Regresión de los fixes anteriores

- Attrs permutados → mismo hash `63cd37b7…` (ya verificado por vos).
- `status:maybe` → `I010`; `%nodeclared` → `G026`.
- Duplicados: `I006` en 1.0, `I002` en 0.1.
- `※` como clave en `$0` → ahora `U003` (antes `I050`; el vector `I_I050` acepta ambos — diagnóstico más temprano del mismo defecto).

### Ya conocidos — no re-reportar

`cortex --help` sin implementar (E-0212) · artefacto Go stale `0.1.0-go` (E-0211) · los emisores nuevos son Python-only hasta E-0224 (port + vectores inválidos a go/node/rs/bash).

### Punto ciego que nadie ha probado

`from-hcortex` con homoglifo — **ya verificado, es un gap real**: compilar un HCORTEX cuyo encabezado `### USR:аdmin` contenga cirílico emite `USR:аdmin` de vuelta con **exit 0, sin diagnóstico**. El guard aguanta al re-parsear (`validate` sobre la salida → `U003` @5:0), pero el compilador no chequea su propia salida — emite fuente que ningún parser 1.0 acepta. **Resuelto (Opción A del Arquitecto):** `compile_hcortex_slots` ahora re-parsea su salida canónica y falla con el diagnóstico del parser si no valida — el compilador nunca emite fuente inválida. Norma: `CORTEX-SPEC-1.0` §8.1. Verificado: `### USR:аdmin` → `U003` exit 1; roundtrip 100/100 sobre corpus 1.0/slots.

Vector listo (el `###` lleva `а` cirílica U+0430):

```markdown
<!-- HCORTEX v=1.0 t=canonical k=corpus -->

<!-- glossary -->
$0:KERNEL
$0:format{cortex:1.0,encoding:UTF-8}
USR:u{type:attrs,weight:M,focus:role,desc:"user",fields:"role:atom"}

<!-- /glossary -->

## §1: USERS

<!-- schema:1 -->
### USR:аdmin
| role |
|---|
| owner |

<!-- /schema:1 -->
```

`python3 -m codec_cortex from-hcortex` sobre ese archivo debe dar `U003` exit 1 (pre-fix: emitía `USR:аdmin` con exit 0). Bonus adversarial: NFD vs NFC en *contenido* (debe pasar — C14N normaliza NFC). El corpus slots sumó el vector permanente `I_U003_homoglyph_name`.


---

## Anexo Alfred 2026-11-04 — paridad de superficies alcanzada

Los emisores portados a las 5 superficies, vector a vector con hashes idénticos:

| Vector | python | go | node | rust | bash |
|---|---|---|---|---|---|
| `U003` homoglifo (idea/attr/label/decl/contrato) | x | x | x | x | x |
| `G014` enum value no-atom | x | x | x | x | x |
| `G026` referencia `%enum` no declarada | x | x | x | x | x |
| `I010` valor fuera de dominio (microtoken expandido) | x | x | x | x | x |
| `I002`/`I006` dirección duplicada | x | x | x | x | x |
| Attrs permutados → mismo hash `63cd37b7…` | x | x | x | x | x |
| `from-hcortex` homoglifo → rechaza (self-validation) | x | x | x | x | x |

Fixes colaterales encontrados durante el port:
- Go/Node/Rust/Bash: regex de marcador `###` era ASCII-only → la idea homoglifa se *descartaba en silencio*; ahora Unicode-aware (`[\p{L}\p{N}_-]`).
- Bash: `c14n-hash` hasheaba bytes crudos → ahora canónico con dominio `CORTEX-C14N-0.2` para 1.0 (paridad con `hash_slots` Python).
- Bash: regex de rangos bajo locale UTF-8 aceptaba `ö` en `[a-z]`; aislado con `LC_ALL=C` en `ccx_is_ascii_identifier`/`ccx_is_atom_body`.
- Artefactos Go reconstruidos (`1.0.0-go`, 5 plataformas + SHA256SUMS); binario Rust en `target/release/cortex`.

Caveat honesto: la suite `v10_oracle_parity` de Rust necesita fixtures externos (`/tmp/oracle/`) que genera la superficie Python — fallo ambiental, no de port; los vectores CLI directos pasan.

— Alfred
