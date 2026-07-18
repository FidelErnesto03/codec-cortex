# Codec-CORTEX — API del Parser Python

Guía de uso para desarrolladores. El paquete `codec-cortex` se instala desde PyPI.

---

## Instalación

```bash
pip install codec-cortex
```

Requiere Python 3.10+. Sin dependencias externas.

## Módulos públicos

### `codec_cortex.parser` — Parseo de CORTEX

```python
from codec_cortex.parser import parse_cortex

doc = parse_cortex(texto_cortex)
# doc es un objeto Document con:
#   doc.format       → metadatos (version, encoding, language, type)
#   doc.sections     → lista de Section
#   doc.glossary     → glosario de sigilos declarados
#
# Cada Section tiene:
#   section.title    → string (ej. "OBJETIVOS" o "")
#   section.id      → int (1, 2, 3...)
#   section.ideas   → lista de Idea
#
# Cada Idea tiene:
#   idea.line        → str con la linea completa
#   idea.section_id  → int
#   idea.is_valid    → bool
```

Ejemplo:

```python
from codec_cortex.parser import parse_cortex

cortex = open("documento.cortex").read()
doc = parse_cortex(cortex)

for sec in doc.sections:
    print(f"Seccion {sec.id}: {sec.title}")
    for idea in sec.ideas:
        print(f"  {idea.line[:80]}")
```

### `codec_cortex.c14n` — Canonicalización (C14N)

```python
from codec_cortex.c14n import canonicalize

canon = canonicalize(doc)
# canon es un string con la representacion canonica
# Mismos bytes para mismo significado semantico
```

Útil para:
- Hashing determinista de documentos CORTEX
- Verificar identidad semantica entre dos documentos
- Comparar implementaciones

### `codec_cortex.hcortex` — Render y compilación HCORTEX

```python
from codec_cortex.hcortex import render_hcortex, compile_hcortex

# CORTEX → HCORTEX (humano)
hc = render_hcortex(doc)
# hc es un string markdown con 5 esquemas emparejados:
# <!-- table:1 --> ... <!-- /table:1 -->
# <!-- prose:2 --> ... <!-- /prose:2 -->

# HCORTEX → CORTEX (compilacion inversa)
doc2, diagnosticos = compile_hcortex(hc_string)
# diagnosticos es una lista de advertencias (no errores)
# doc2 es un Document como el original
```

### `codec_cortex.harness` — Suite de validación

```python
from codec_cortex.harness import run_all_tests

reporte = run_all_tests(c14n_dir, hcortex_dir)
# reporte contiene resultados de F3 (C14N) y F4 (HCORTEX)
```

## Flujo de trabajo típico

```python
from codec_cortex.parser import parse_cortex
from codec_cortex.hcortex import render_hcortex, compile_hcortex
from codec_cortex.c14n import canonicalize

# 1. Parsear CORTEX
doc = parse_cortex(texto_cortex)

# 2. Mostrar a un humano
hc = render_hcortex(doc)
print(hc)  # Markdown con esquemas emparejados

# 3. El humano edita el HCORTEX...
# 4. Compilar de vuelta
doc_vuelto, diags = compile_hcortex(hc_editado)

# 5. Verificar que el significado se preservo
hash1 = canonicalize(doc)
hash2 = canonicalize(doc_vuelto)
son_iguales = (hash1 == hash2)
```

## Referencias

- [skill/codec-cortex.skill.md](../skill/codec-cortex.skill.md) — El estándar en CORTEX, autocontenido
- [QUICKSTART.md](QUICKSTART.md) — Guía de inicio rápido
- [authoring/custom-sigils.md](authoring/custom-sigils.md) — Crear sigilos personalizados
- [authoring/hcortex-templates.md](authoring/hcortex-templates.md) — Plantillas HCORTEX
