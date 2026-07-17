# Fase 3 — Carta de Navegación para Canonicalización

**Document ID:** `CORTEX-F3-CHARTER-001`
**Standard version:** `0.1`
**Status:** `pre-phase-guidance`
**Date:** `2026-07-17`
**Authority basis:** `CORTEX-CONSTITUTION-001`, `CORTEX-SPEC-0.1-DRAFT-REAL-001`
**Inputs:** Mini Gate F2 (BLP-003 + BLP-005), correcciones de especificación (BLP-004), hallazgo F2-F001
**Language:** español

---

## 1. Propósito

Este documento establece los lineamientos, restricciones y orden de construcción para Fase 3 del estándar CORTEX. No es la especificación de canonicalización — es la carta de navegación que guía su construcción, basada en todo lo aprendido durante Fase 2 y los experimentos de implementabilidad.

La Fase 3 debe responder: **¿cuándo dos documentos CORTEX son equivalentes?** La canonicalización C14N-0.1 es el fundamento del roundtrip CORTEX↔HCORTEX — no una certificación de parsers independientes.

---

## 2. Invariantes — lo que NO cambia en Fase 3

Extraído de la Constitution, Charter y decisiones D-001 a D-017 de Fase 2 REAL. Estas propiedades SON SAGRADAS — ninguna decisión de Fase 3 puede violarlas.

### 2.1 Invariantes estructurales

| # | Invariante | Fuente | Riesgo si se viola |
|---|---|---|---|
| I1 | La Idea es la unidad fundamental del AST, no un value genérico | D-001 | El formato se convierte en JSON con otra sintaxis |
| I2 | Los 5 shapes se conservan: attrs, attrs-pos, cuerpo, bloque, relacion | D-005 | HCORTEX pierde proyección directa |
| I3 | El glosario $0 es primero, único y estructural | I1 de spec §33 | Portabilidad colapsa |
| I4 | El documento transporta el vocabulario usado | I2 de spec §33 | Dependencia de registros externos |
| I5 | Toda línea regular expresa una Idea principal | I3 de spec §33 | Se pierde el codec ideático |
| I6 | No existe encoded wrapper como octavo shape | D-005 | RECONSTRUCTED intentó introducirlo |
| I7 | Solo el focus lleva comillas — el resto son atoms | BLP-004 | F2-F001 validado experimentalmente |
| I8 | El orden observado se preserva (aunque no todo orden sea significativo) | D-006 | El AST perdería información de source |

### 2.2 Invariantes operacionales

| # | Invariante | Fuente |
|---|---|---|
| O1 | El AST sirve al formato, no al revés — no es una serialización genérica | D-015 |
| O2 | No existe pérdida silenciosa | Art. V Constitution |
| O3 | La canonicalización es idempotente: canon(canon(x)) == canon(x) | Art. VI Constitution |
| O4 | HCORTEX-CANONICAL deriva del AST, no constituye segunda ontología | Art. VII Constitution |
| O5 | El algoritmo no depende de LLM, heurísticas, red, fecha ni locale | Art. IV Constitution |
| O6 | El Core no conoce ontologías de agente (KNW, OBJ, FCS, WRK son perfiles) | Art. II Constitution |
| O7 | Un derivado NO DEBE modificarse como sustituto del canon | Art. XVIII Constitution |

---

## 3. Decisiones pendientes de Fase 3

Extraído de spec §31 (Frontera con Fase 3) y corregido por los experimentos.

### 3.1 Orden canónico (F3-A) — FUNDACIÓN

**Problema:** Dos documentos con el mismo contenido pero distinto orden deben producir el mismo hash.

**Decisiones:**

#### 3.1.1 Secciones
- Las secciones mantienen el orden observado. El orden de secciones es comunicativamente significativo (spec §26.3).
- **NO** se reordenan alfabéticamente.

#### 3.1.2 Ideas dentro de una sección
- Las Ideas mantienen el orden observado. El orden de Ideas es comunicativamente significativo.
- **NO** se reordenan alfabéticamente.

#### 3.1.3 Pares attrs dentro de una Idea
- **DECISIÓN REQUERIDA:** ¿orden del contrato o orden de aparición?
- Opción A (contrato): El orden canónico sigue el contrato declarado en $0. Los campos aparecen en el orden del `fields`/`pos`.
- Opción B (aparición): Se conserva el orden en que aparecen en la fuente.
- **Recomendación:** Opción A — consistente con la regla de orden de spec §14.4. Reduce sorpresas.

#### 3.1.4 Declaraciones de $0
- **DECISIÓN REQUERIDA:** ¿orden alfabético, orden de tipo, u orden de aparición?
- Propuesta: `$0:format` primero, luego enums (alfabético), luego microtokens (alfabético), luego namespaces (alfabético), luego extensiones (alfabético), luego declaraciones de sigilos (alfabético por symbol).
- **Recomendación:** Este orden minimiza sorpresas y es independiente del autor.

#### 3.1.5 Extensiones asociadas al mismo owner
- **DECISIÓN REQUERIDA:** ¿orden de aparición o alfabético por namespace:id:version?
- **Recomendación:** Alfabético por namespace:id:version. Son metadata, no contenido.

#### 3.1.6 Riesgo del orden canónico

**Advertencia del experimento:** El parser Go de BLP-003 y el Rust de BLP-005 producen los pares attrs en distinto orden. Esto no es un bug — la spec actual lo permite. Pero significa que **dos implementaciones conformantes pueden producir bytes distintos para el mismo documento**. Sin orden canónico, el hash canónico es imposible.

**Validación:** Una vez definido, los 40 casos válidos del corpus deben producir los mismos bytes canónicos en Rust y Python.

---

### 3.2 Whitespace y newlines (F3-B)

**Problema:** El shape `cuerpo` y `bloque` pueden tener newlines iniciales/finales y padding que varían entre autores.

**Decisiones:**

#### 3.2.1 Cuerpo multilínea
- **DECISIÓN REQUERIDA:** ¿normalizar o preservar?
- El contenido del cuerpo es semántico — `\n` extra al inicio/fin puede ser intencional o accidental.
- **Recomendación:** Normalizar: trim de exactamente un `\n` al inicio y un `\n` antes del `}` de cierre. Si hay blank lines adicionales, se preservan (son contenido intencional).

#### 3.2.2 Bloque verbatim
- **DECISIÓN REQUERIDA:** Normalización distinta de cuerpo.
- **Recomendación:** Normalización MÍNIMA. El bloque contiene texto verbatim (código, PUML). Solo normalizar el newline de cierre antes de `}`. El contenido interno se preserva exactamente.

#### 3.2.3 Indentación
- CORTEX 0.1 no define indentación. El whitespace horizontal al inicio de línea NO es normativo.
- **Recomendación:** Ignorar espacios/tabs iniciales y finales de línea durante canonicalización.

#### 3.2.4 Riesgo de whitespace

**Advertencia del experimento:** El caso V011 (cuerpo_multiline) y V029 (body_empty_lines) fallaron en Go porque el parser no manejaba correctamente los newlines. La spec §13.3 describe la forma multilínea pero no especifica si los blank lines son significativos. Sin esta decisión, dos implementaciones producirán ASTs diferentes.

**Validación:** V011, V012, V029 deben producir ASTs equivalentes en cualquier implementación después de F3.

---

### 3.3 Microtokens (F3-C)

**Problema:** ¿El AST canónico expande el microtoken o preserva el lexema?

```cortex
$0:micro_cur{expand:current}
...
FCS:focus{what:"Objetivo",status:cur}
```

| Enfoque | AST de `cur` | Ventaja | Desventaja |
|---|---|---|---|
| **Expandir** | `{"value": "current", "lexeme": "cur"}` | Equivalencia semántica directa | Pierde información de source |
| **Preservar** | `{"value": "cur", "micro": "current"}` | Conserva intención del autor | Dos representaciones para el mismo valor |

**Recomendación:** Expandir para canonicalización. El valor canónico es `"current"`; el lexema se preserva como metadata opcional (source preservation). Esto es consistente con Art. VI (determinismo) — el mismo valor debe producir el mismo AST independientemente de cómo se escribió en la fuente.

**Validación:** V005 (microtoken_attrs) y V006 (microtoken_positional) deben pasar con el mismo AST después de F3.

---

### 3.4 Números canónicos (F3-D)

**Problema:** ¿`0.75` y `0.750` son el mismo valor?

**Decisiones:**

#### 3.4.1 Integer
- Sin `+`, sin leading zeros. `03` → inválido. `0` y `3` son canónicos.

#### 3.4.2 Decimal
- Forma canónica: `[0-9]+\.[0-9]+` (al menos un dígito a cada lado del punto).
- `0.75` → canónico. `.75` → inválido. `0.750` → canónico como `0.750` (la precisión es significativa).
- **DECISIÓN REQUERIDA:** ¿Normalizar `0.750` → `0.75` (pérdida de precisión) o preservar (precisión exacta)?
- **Recomendación:** Preservar la representación exacta. `0.75` y `0.750` son valores distintos. Si la canonicalización los unifica, se pierde la distinción que el autor eligió explícitamente. La spec actual dice "El AST conserva su representación decimal exacta como texto" (§17.4).

#### 3.4.3 Riesgo de números

**Advertencia del experimento:** Ningún caso del corpus prueba `0.750` vs `0.75`. Agregar un vector de conformidad para esta decisión.

---

### 3.5 Unicode NFC (F3-E)

**Problema:** Caracteres como "é" pueden representarse como un solo code point (NFC) o como dos (NFD). Visualmente idénticos, bytes distintos.

**Decisión:**
- El AST canónico DEBE normalizar a NFC (spec §23).
- El parser DEBE emitir `W610_UNICODE_NORMALIZED` cuando normaliza.
- El hash canónico opera sobre la forma NFC.
- **EXCEPCIÓN:** Bloque verbatim (`bloque`) preserva el contenido original — no normaliza.

**Validación:** V017 (unicode) debe pasar con cualquier forma de entrada.

---

### 3.6 Source preservation (F3-F) — DIFERIDO

**Decisión:** La preservación de source (comentarios, whitespace original, lexemas exactos) NO es requisito normativo de CORTEX Standard 1.0. Es una capacidad opcional de implementaciones, documentada como tooling.

**Razón:** Es ortogonal a la canonicalización. Un parser puede preservar source en su AST interno, pero el output canónico (hash, HCORTEX, comparación) opera sobre el AST normalizado.

**Diferir a:** Fase 5 (implementación de referencia) o tooling específico.

---

### 3.7 Hash canónico (F3-G) — CULMINACIÓN

**Problema:** ¿Cómo demostrar que dos documentos son equivalentes?

**Algoritmo propuesto:**

```
bytes_fuente → parse → AST lógico
    → aplicar orden canónico (F3-A)
    → normalizar whitespace (F3-B)
    → expandir microtokens (F3-C)
    → normalizar números (F3-D)
    → normalizar NFC (F3-E)
    → serializar AST a bytes UTF-8 (orden definido, sin whitespace extra)
    → SHA256(bytes)
```

**Propiedades:**
1. Idempotente: `canon(canon(x)) == canon(x)`
2. Determinista: misma entrada + misma versión = mismo hash
3. Neutral: no depende del lenguaje de implementación
4. Verificable: dos implementaciones independientes producen el mismo hash

**RESTRICCIÓN:** El hash se define DESPUÉS de resolver F3-A a F3-E. Si se define antes, cualquier cambio en el orden canónico invalida el hash.

---

## 4. Pipeline de canonicalización

```text
Fuente .cortex
    │
    ▼
┌──────────────────┐
│ 1. Parse         │  ← Fase 2 (existente)
│    → AST lógico  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 2. Normalizar    │  ← Fase 3
│    → Orden       │  (F3-A)
│    → Whitespace  │  (F3-B)
│    → Microtokens │  (F3-C)
│    → Números     │  (F3-D)
│    → Unicode NFC │  (F3-E)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 3. Serializar    │  ← Fase 3
│    → AST canónico│
│    a bytes UTF-8 │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 4. Hash (SHA256) │  ← Fase 3
│    = fingerprint │  (F3-G)
│    del documento │
└──────────────────┘
```

**Nota:** El paso 2 no modifica el AST fuente — produce un AST derivado canónico. El AST original se conserva para source preservation (F3-F, diferido).

---

## 5. Criterios de éxito de Fase 3

| # | Criterio | Verificación |
|---|---|---|
| CE-1 | La canonicalización es idempotente | `canon(canon(x)) == canon(x)` en los 40 casos válidos |
| CE-2 | Dos implementaciones producen los mismos bytes canónicos | Python + Rust producen SHA256 idéntico para cada caso del corpus |
| CE-3 | El orden canónico de $0 es determinista e independiente del autor | Reordenar $0 manualmente → mismo hash |
| CE-4 | Microtokens expandidos producen el mismo AST que su valor expandido | `status:cur` con `micro_cur` → mismo que `status:current` sin microtoken |
| CE-5 | Unicode NFC: misma string en NFC y NFD → mismo hash | V017 probado con ambas formas |
| CE-6 | Loss report vacío para transformaciones no destructivas | `STD-3` no emite warning falso |
| CE-7 | HCORTEX-CANONICAL puede reconstruir el AST original desde el canónico | Roundtrip estructural completo |

---

## 6. Riesgos conocidos

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Definir orden canónico antes de probarlo con implementaciones reales | Alto — puede ser impracticable | Validar orden canónico contra Rust + Python antes de ratificar |
| Normalización de whitespace en cuerpo pierde intención del autor | Medio — documento visual vs semántico | Distinguir cuerpo (semántico) de bloque (verbatim) |
| Hash canónico cambia porque se descubre una ambigüedad en F3-A | Alto — invalida fingerprints | No publicar hash hasta que F3-A a F3-E estén ratificados |
| Microtokens expandidos rompen equivalencia con documentos que no usan microtokens | Bajo — la expansión es canónica; el original se conserva en source preservation | La canonicalización no borra el original |

---

## 7. Dependencias entre fases de Fase 3

```text
F3-A (Orden) ──────────────────────────────┐
F3-B (Whitespace) ───────────────────────┐ │
F3-C (Microtokens) ───────────────────┐ │ │
F3-D (Números) ────────────────────┐  │ │ │
F3-E (Unicode NFC) ──────────────┐ │  │ │ │
                                 ▼ ▼  ▼ ▼ ▼
                            F3-G (Hash)
                                 │
F3-F (Source preservation) ──────┘ (independiente, diferido)
```

**Orden de construcción recomendado:**

1. F3-A (Orden) → base de todo
2. F3-C (Microtokens) → afecta al AST directamente
3. F3-D (Números) → simple, pocas aristas
4. F3-B (Whitespace) → requiere cuidado pero no afecta estructura
5. F3-E (Unicode) → independiente, puede ir en paralelo
6. F3-G (Hash) → solo cuando los 5 anteriores estén estables
7. F3-F (Source preservation) → diferido a Fase 5 o posterior

---

## 8. Referencias

- `CORTEX-SPEC-0.1.md` §31 — Frontera con Fase 3
- `CORTEX-CONSTITUTION-001` Art. IV, V, VI, VII, XVIII
- `CORTEX-CHARTER-001` §5 (propiedades obligatorias), §13 (indicadores de éxito)
- `review/GATE-F2-V2-REPORT.md` — Resultados del experimento de implementabilidad
- `review/PHASE-2-FINDING-F001-QUOTES.md` — Hallazgo de comillas
- `review/PHASE-2-DESIGN-DECISIONS.md` — Decisiones D-001 a D-017
