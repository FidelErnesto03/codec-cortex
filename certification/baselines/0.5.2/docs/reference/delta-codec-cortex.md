# Delta Técnico — codec-cortex v0.4.1 → v0.4.3

> **Propósito:** Informe detallado de cambios introducidos en CODEC-CORTEX entre la
> versión empaquetada en PyPI (v0.4.1, commit `7139d3a`) y la versión local HEAD
> (v0.4.3, commit `9443718`). Proyectos dependientes (`arqux`, `nomos-gov`, etc.)
> deben adaptar su integración según lo documentado aquí.

| Contexto | Valor |
|---|---|
| **Paquete** | `codec-cortex` |
| **Versión PyPI** | v0.4.1 (6f1d4f0) |
| **Versión local** | v0.4.3 (9443718) |
| **Delta commits** | 3 commits sin publicar |
| **Fecha análisis** | 2026-07-09 |

**Versión pip reportada:** `0.4.3.dev1+g19628042f` — el tag `dev1` + commit `1962804` indica
que la versión instalada editable está entre `v0.4.1` y `v0.4.3`.

---

## §1: Resumen de cambios

| # | Commit | Tag | Módulos afectados | Tipo |
|---|---|---|---|---|
| 1 | `1962804` | — | Varios (ruff lint) | Refactor |
| 2 | `2052dd2` | `v0.4.2` | `core/ast.py`, `core/lexer.py`, `core/parser.py`, `core/validator.py` | **API CHANGE** |
| 3 | `9443718` | `v0.4.3` | `core/repair.py` **(nuevo)**, `crud/transactions.py` | **FEATURE** |

---

## §2: Cambio 1 — Ruff lint cleanup

| Atributo | Valor |
|---|---|
| **Commit** | `1962804` |
| **Impacto API** | Ninguno |
| **Requiere adaptación** | No |

**Resumen:** Limpieza de imports no utilizados, estilo de código. Sin cambios en
la superficie pública.

---

## §3: Cambio 2 — Local glossary sigils (v0.4.2)

| Atributo | Valor |
|---|---|
| **Commit** | `2052dd2` |
| **Impacto API** | Alto |
| **Requiere adaptación** | Sí |

### §3.1: Secciones decimales (`$2.1`, `$3.5`)

**Antes:** El parser rechazaba identificadores de sección con punto decimal.
`normalize_section_id()` usaba `isdigit()` para validar, que falla en cadenas
como `"2.1"`.

**Después:** `normalize_section_id()` y `looks_like_section_header()` ahora usan
`is_section_number()` que acepta puntos: `"2.1"` → `$2.1`.

**Impacto:** Archivos `.cortex` con secciones decimales ahora se parsean
correctamente. Cualquier proyecto que genere o espere secciones `$N` sin decimal
no se rompe, pero debe estar preparado para recibir secciones decimales desde
el parser.

### §3.2: Puntos en nombres de entrada (`HDL:workspace.init`)

**Antes:** La regex del lexer solo aceptaba `[A-Za-z_][A-Za-z0-9_]*` para nombres
de entrada. Un punto en el nombre (`workspace.init`) causaba error de parseo.

**Después:** La regex cambió a `[A-Za-z_][A-Za-z0-9_.]*` — los puntos son
permitidos en nombres de entrada.

**Impacto:** Handlers MCP (ej. `HDL:workspace.init`, `HDL:blueprint.create`) ahora
se pueden expresar como nombres de entrada literales sin necesidad de
escapar o convertir.

### §3.3: `parse_attrs_body()` — claves numéricas y mapas anidados

**Antes:** Las claves en attrs body debían empezar con letra (`[A-Za-z_]`).
Valores anidados (`{...}`) no estaban soportados. Bare values solo
parseaban tipos simples (int, float, bool, null, string).

**Después:**
- Claves aceptan `[A-Za-z0-9_]` — ahora pueden empezar con dígito
  (ej. `1_explain`, `2_status`)
- Mapas anidados `{...}` como valores son parseados recursivamente
  (ej. `created:{manifest:"x", skills:"y"}`)
- Bare value parsing fue extraído a función interna `parse_bare()`:
  maneja true/false, null/none/nil/undefined, int, float, string
- El parser de valores respeta profundidad de `{}` y strings escapados,
  lo que permite comas dentro de valores anidados

**Impacto:** Estructuras de datos más ricas en attrs. Proyectos que inyecten
attrs bodies deben asegurar que sus generadores respeten la nueva sintaxis.
La función `parse_bare()` es interna (no exportada), pero proyectos que
reescriban el parsing de attrs pueden beneficiarse.

### §3.4: `attrs-pos` sin contrato → fallback a attrs body

**Antes:** En `_parse_entry_values()`, un sigilo `attrs-pos` sin contrato en `$0`
generaba error `E007_ATTRS_POS_CONTRACT_MISSING` y asignaba `value={}`.
En `validate()`, se reportaba el mismo error.

**Después:**
- `_parse_entry_values()`: sin contrato, parsea el body como attrs normal
  (`parse_attrs_body(body)`) en lugar de devolver `{}`
- `validate()`: solo reporta `E007` si el valor parseado NO es un dict
  (es decir, si efectivamente no se pudo interpretar como attrs)

**Impacto:** Sigilos `attrs-pos` sin contrato ahora producen datos útiles en
lugar de silencio. Proyectos que dependían de `E007` como bloqueante deben
revisar su lógica de validación — el error ahora solo aparece cuando el
valor es genuinamente inválido, no por falta de contrato.

### §3.5: Tests de regresión agregados

Nuevo archivo `tests/test_local_glossary_sigils.py` con 5 tests:

| Test | Verifica |
|---|---|
| `test_local_sigil_attrs_accepts_numbered_keys` | Claves numéricas, dots en nombres |
| `test_decimal_section_headers_are_parsed` | `$2.1` como sección válida |
| `test_local_attrs_pos_without_contract_accepts_attrs_body` | attrs-pos → attrs fallback |
| `test_nested_attrs_maps_are_parsed` | Mapas `{...}` anidados |
| `test_undeclared_local_sigil_still_reports_e003` | E003 se sigue reportando |

---

## §4: Cambio 3 — Auto-repair E032/E034 (v0.4.3)

| Atributo | Valor |
|---|---|
| **Commit** | `9443718` |
| **Impacto API** | Medio |
| **Requiere adaptación** | Sí (revisar flujo force=True) |

### §4.1: Nuevo módulo `cortex.core.repair`

Archivo: `cli/src/cortex/core/repair.py` (149 líneas, nuevo)

**API pública:**

| Función | Firma | Propósito |
|---|---|---|
| `get_default` | `(field: str) → str` | Devuelve default semántico para un campo |
| `missing_fields` | `(entry: Any) → List[str]` | Campos requeridos ausentes en `entry.value` |
| `empty_fields` | `(entry: Any) → List[str]` | Campos requeridos presentes pero vacíos |
| `repair_entry` | `(entry: Any) → Tuple[bool, Dict[str,str]]` | Rellena campos faltantes/vacíos con defaults |
| `repair_doc` | `(doc: Any) → List[Dict[str,Any]]` | Escanea todo el documento y repara |
| `needs_repair` | `(doc: Any) → bool` | True si hay entradas que requieren reparación |
| `has_e032_e034` | `(diagnostics: List[Dict]) → bool` | True si hay errores E032 o E034 |

**FIELD_DEFAULTS:** 32+ valores por defecto semánticamente neutros:

```
prevention → "not_applicable"    success → "pending"
output → "pending"               cause → "not_specified"
survive → "work"                 status → "active"
priority → "medium"              goal → "pending"
what → "pending"                 phase → "active"
current → "pending"              blocked → "no"
input → "pending"                outcome → "pending"
date → "pending"                 topic → "untitled"
content → "pending"              type → "note"
lesson → "pending"               limit → "pending"
scope → "project"                rule → "pending"
risk → "pending"                 action → "pending"
reason → "pending"               owner → "auto"
statement → "pending"            evidence → "pending"
event → "pending"                result → "pending"
mitigation → "pending"           severity → "medium"
```

### §4.2: `atomic_write_cortex()` modificado

**Archivo:** `cli/src/cortex/crud/transactions.py`

**Antes:** Cuando `force=True`, los errores bypassables se ignoraban pero
los no-bypassables (E032, E034) siempre bloqueaban la escritura,
incluso con `force=True`.

**Después:** Cuando `force=True` y hay errores E032/E034:
1. `has_e032_e034(diagnostics)` detecta los errores reparables
2. `repair_doc(reparsed)` rellena campos faltantes/vacíos con defaults
3. Re-serializa, re-parsea y re-valida el documento
4. Si no quedan errores, escribe normalmente
5. Errores no-bypassables que NO son E032/E034 (ej. secretos) siguen bloqueando

**Comentario actualizado en código:**
> "non-bypassable errors (secrets, critical sigil incompleteness) CANNOT be
> overridden by --force (except via auto-repair above)."

**Impacto:** `atomic_write_cortex(doc, path, force=True)` ahora puede completar
escrituras que antes fallaban con `E032_CRITICAL_SIGIL_INCOMPLETE` o
`E034_CRITICAL_REQUIRED_FIELD_EMPTY`. Los proyectos que usen `force=True`
verán entradas legacy reparadas automáticamente con valores por defecto.
Esto es deseable para migración de brains legacy, pero puede ocultar datos
faltantes si no se revisa el log de reparación.

---

## §5: Cambios adicionales detectados

### §5.1: Versión en `__init__.py`

**Archivo:** `cli/src/cortex/__init__.py`

**Antes:**
```python
__version__ = "0.0.0.dev0"  # fallback
```

**Después:**
```python
__version__ = "0.4.3"  # fallback explícito
```

**Impacto:** La versión reportada por `cortex.__version__` cambia de
`"0.0.0.dev0"` a `"0.4.3"` en instalaciones editable sin `_version.py`.

### §5.2: `pyproject.toml` raíz (no CLI)

**Archivo:** `pyproject.toml` (raíz del repo)

**Antes:** `version = "0.4.1"`

**Después:** `version = "0.4.3"`

### §5.3: Learning Engine v0.2.0 (ya en pip)

**Nota:** El Learning Engine v0.2.0 (commit `0c6b1f0`, 6 módulos nuevos) ya está
incluido en la versión pip (`0.4.3.dev1` incluye este commit). No es parte
del delta reportado aquí.

**Módulos nuevos en v0.2.0 (ya disponibles en pip):**
- `learning/session.py` + `session_cli.py`
- `learning/handlers.py` — auto-detección pre_action/post_action
- `learning/decay.py` — cooling exponencial (half-life 7d)
- `learning/feedback.py` — thresholds adaptativos
- `learning/policy_defaults.py` — perfiles aggressive/conservative/default
- `learning/policy.py` — Fibonacci, cooling, detection, feedback

---

## §6: Guía de adaptación para proyectos dependientes

### Proyectos que llaman `atomic_write_cortex()`

```python
# ANTES (v0.4.1): force=True podía fallar con E032/E034
from cortex.crud.transactions import atomic_write_cortex
result = atomic_write_cortex(doc, path, force=True)
# Podía lanzar o devolver error por LNG sin prevention

# DESPUÉS (v0.4.3): force=True repara automáticamente E032/E034
from cortex.crud.transactions import atomic_write_cortex
result = atomic_write_cortex(doc, path, force=True)
# LNG:mi_lesson sin "prevention" → se rellena con "not_applicable"
# El repair log está disponible en el flujo interno
```

**Acción recomendada:**
- No requiere cambios en el código — el comportamiento es compatible hacia atrás
- Si se desea inspeccionar qué se reparó, importar `repair_doc()` y
  `has_e032_e034()` desde `cortex.core.repair` y ejecutar pre-validación
- Revisar que los valores default (`not_applicable`, `pending`) sean
  aceptables para la lógica de negocio del proyecto

### Proyectos que parsean attrs bodies

```python
# ANTES: claves debían empezar con letra
value = parse_attrs_body('key:"val", 2:"num"')
# Error: InvalidAttrsError por clave "2"

# DESPUÉS: claves pueden empezar con dígito
value = parse_attrs_body('key:"val", 2:"num"')
# OK: {"key": "val", "2": "num"}

# NUEVO: mapas anidados
value = parse_attrs_body('created:{name:"test", version:"1"}')
# OK: {"created": {"name": "test", "version": "1"}}
```

**Acción recomendada:**
- Si el proyecto genera attrs bodies, puede usar claves numéricas y
  mapas anidados sin restricción
- Si el proyecto consume attrs bodies, debe manejar valores que sean
  `dict` anidados (antes solo str/int/float/bool/None)

### Proyectos que dependen de validación `E007`

```python
# ANTES: attrs-pos sin contrato → E007 siempre
# DESPUÉS: attrs-pos sin contrato → E007 solo si value no es dict
```

**Acción recomendada:**
- Si el proyecto bloqueaba escritura por E007, ahora debe verificar
  si el error persiste después del fix (puede haber desaparecido)
- Si el proyecto usaba E007 como señal de "contrato faltante", debe
  usar `doc.glossary.contract_for(sigil) is None` en su lugar

### Proyectos que generan secciones

```python
# NUEVO: secciones decimales son válidas
section_id = normalize_section_id("2.1")
# Devuelve "$2.1" (antes podía producir "$2.1" o error)
```

**Acción recomendada:**
- Si el proyecto normaliza section IDs, `normalize_section_id()` ahora
  preserva decimales
- Si el proyecto espera solo secciones `$N` (sin decimal), debe estar
  preparado para recibir `$N.M` desde el parser

### Proyectos que usan nombres de entrada con puntos

```python
# NUEVO: nombres con punto son válidos
# HDL:workspace.init → entry.name = "workspace.init"
```

**Acción recomendada:**
- Si el proyecto genera nombres de entrada, ahora puede usar puntos
- Si el proyecto hace lookup por nombre exacto, debe considerar que
  el nombre puede contener puntos

---

## §7: Resumen de compatibilidad

| Aspecto | Compatibilidad | Acción necesaria |
|---|---|---|
| `atomic_write_cortex(force=True)` | ✅ Hacia atrás | Ninguna (beneficio automático) |
| `parse_attrs_body()` — claves numéricas | ✅ Hacia atrás | Ninguna (sintaxis extendida) |
| `parse_attrs_body()` — mapas anidados | ✅ Hacia atrás | Ninguna (nueva capacidad) |
| `attrs-pos` sin contrato | ⚠️ Comportamiento cambiado | Validar lógica de E007 |
| Secciones decimales `$2.1` | ✅ Hacia atrás | Preparar consumers |
| Nombres con punto | ✅ Hacia atrás | Preparar lookup |
| `E032`/`E034` con `force=True` | ⚠️ Ahora repara | Revisar defaults |
| `NormalizeSectionId()` | ⚠️ Comportamiento extendido | Validar si se usa como key |
| `REQUIRED_FIELDS` | Sin cambios | Ninguna |
| `validate()` | Sin cambios | Ninguna |

---

## §8: Archivos nuevos

| Archivo | Líneas | Propósito |
|---|---|---|
| `cli/src/cortex/core/repair.py` | 149 | Auto-repair de E032/E034 con force=True |
| `cli/src/tests/test_local_glossary_sigils.py` | 111 | Tests de sigilos locales, decimales, anidados |

---

## §9: Inconvenientes conocidos

1. **`FIELD_DEFAULTS` no es configurable**: Los valores default están hardcodeados
   en `repair.py`. Proyectos que necesiten defaults diferentes deben envolver
   `atomic_write_cortex()` o copiar el módulo.

2. **Auto-repair no produce warning visible**: La reparación ocurre silenciosamente
   dentro de `atomic_write_cortex()`. No hay log de reparación en la salida
   estándar. Los proyectos deben inspeccionar manualmente si quieren visibilidad.

3. **`parse_bare()` es función interna**: No exportada desde `cortex.core.parser`.
   Proyectos que necesiten parseo de bare values deben duplicar la lógica o
   solicitar su exportación.

4. **Dots en nombres de entrada no retrocompatibles con selectors antiguos:**
   Selectors que usen el nombre como parte de una ruta (ej. `HDL:workspace.init`)
   pueden confundirse con selectores anidados. Verificar la implementación
   de `cortex.crud.selectors` para compatibilidad.

---

*Documento generado por Jarvis (executor) bajo governance ArqUX.*
*CODEC-CORTEX v0.4.1 → v0.4.3 — 2026-07-09*
