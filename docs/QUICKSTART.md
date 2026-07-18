# CODEC-CORTEX — Inicio rápido

**5 minutos para entender CORTEX y escribir tu primer documento.**

---

## Paso 1: Entiende la idea

CORTEX es un formato donde **cada línea expresa una idea**. Las ideas tienen un tipo (sigilo), un nombre y atributos.

```cortex
SIGILO:nombre{atributos}
```

Ejemplo real:

```cortex
OBJ:mi_objetivo{goal:"Aprender CORTEX.",status:current}
```

## Paso 2: Arma un documento

Todo documento CORTEX tiene 3 partes:

1. **$0** — Glosario (declara los sigilos que se usaran)
2. **$N: TITULO** — Secciones (agrupan ideas por contexto)
3. **Las ideas** — Cada una en su linea

```cortex
$0
$0:format{cortex:0.1,encoding:UTF-8,language:es}
TAR:task{type:attrs,fields:"desc:text|estado:%state",focus:desc,schema:table}

$1: TAREAS
TAR:comprar{desc:"Comprar pan",estado:pendiente}
TAR:llamar{desc:"Llamar al medico",estado:hecho}
```

## Paso 3: Crea un sigilo personalizado

En $0, declara:

```cortex
TAR:task{type:attrs,weight:M,fields:"desc:text|estado:%state|prioridad:%prio",focus:desc,schema:table,desc:"Tarea del proyecto"}
```

Los campos:
- **type:** attrs, cuerpo, bloque, relacion o attrs-pos
- **fields:** contrato de campos (tipo:text, number, %bool o %enum)
- **focus:** campo principal
- **schema:** prose, table, list, check o diagram
- **desc:** descripcion del sigilo

## Paso 4: Crea HCORTEX (para humanos)

CORTEX es para la IA. HCORTEX es su traduccion a formato humano.

```markdown
<!-- HCORTEX v=0.1 t=canonical k=documento -->

## §1: TAREAS

<!-- table:1 -->
| Comprar pan | pendiente |
| Llamar al medico | hecho |
<!-- /table:1 -->
```

Los 5 esquemas:
- **prose:N** — Texto libre
- **table:N** — Tabla con pipes
- **list:N** — Lista con bullets
- **check:N** — Checklist
- **diagram:N** — PUML en fence

## Paso 5: Valida

```bash
pip install codec-cortex
python3 -c "
from codec_cortex.parser import parse_cortex
doc = parse_cortex(open('mi_documento.cortex').read())
print(f'OK — {len(doc.sections)} secciones')
"
```

## Siguientes pasos

- [docs/authoring/custom-sigils.md](custom-sigils.md) — Creacion avanzada de sigilos
- [docs/authoring/hcortex-templates.md](hcortex-templates.md) — Plantillas HCORTEX
- [docs/standard/CORTEX-SPEC-0.1.md](../standard/CORTEX-SPEC-0.1.md) — Especificacion completa
- [skill/codec-cortex.skill.md](../../skill/codec-cortex.skill.md) — Skill autocontenido
