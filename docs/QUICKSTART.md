# CODEC-CORTEX — Inicio rápido

**Cinco minutos para entender CORTEX 1.0, escribir tu primer documento y
verificarlo con las herramientas reales.**

---

## Paso 1: la idea

CORTEX es un formato donde **cada línea física expresa una idea**. Una idea
tiene un sigilo (su tipo), un nombre y un payload: atributos, celdas, cuerpo o
bloque.

```cortex
SIGILO:nombre{atributos}
SIGILO:nombre|celda1|celda2
SIGILO:nombre{
cuerpo o bloque verbatim
}
```

## Paso 2: un documento

Todo documento `cortex:1.0` tiene tres partes:

1. **`$0` — glosario.** Declara la capa (`$0:KERNEL` o `$0` desnudo), la versión
   (`$0:format{cortex:1.0,encoding:UTF-8}`) y los sigilos que se usan.
2. **Secciones `$N`.** Agrupan ideas. Admite título y capa: `$1: TAREAS:CORE`.
3. **Las ideas**, una por línea.

```cortex
$0:KERNEL
$0:format{cortex:1.0,encoding:UTF-8,language:es}
$0:enum_state{values:"pendiente|hecho"}
TAR:task{type:attrs,weight:M,focus:desc,desc:"Tarea simple",fields:"desc:text|estado:%state"}
$1: TAREAS:DATA
TAR:comprar{desc:"Comprar pan",estado:pendiente}
TAR:llamar{desc:"Llamar al medico",estado:hecho}
```

La cabecera del glosario es **`$0` o `$0:<CAPA>`**. Un título detrás de `$0:` no
pertenece al lenguaje: se rechaza con `G042_GLOSSARY_HEADER_INVALID`.

## Paso 3: un sigilo propio

Se declara en `$0` y se usa en las secciones:

```cortex
TAR:task{type:attrs,weight:M,focus:desc,desc:"Tarea de proyecto",fields:"desc:text|estado:%state|prioridad:int?",open:true}
```

| Atributo | Qué define |
|---|---|
| `type` | `attrs`, `attrs-pos`, `relacion`, `cuerpo` o `bloque` |
| `fields` / `pos` | contrato de campos (tipo: `text`, `int`, `bool`, `%enum`) |
| `focus` | campo principal (el que se renderiza destacado) |
| `open` | `true` permite campos fuera del contrato |
| `desc` | etiqueta de 1–3 palabras (clasifica, no documenta) |

Los tipos de campo son el contrato de aridad: una idea `attrs-pos` o `relacion`
con más celdas de las declaradas falla con `I012_POSITIONAL_ARITY`.

## Paso 4: HCORTEX (para humanos)

CORTEX es para la IA; HCORTEX es su traducción determinista. Se genera con una
sola orden y **nunca se edita a mano si se espera roundtrip**:

```bash
python -m codec_cortex to-hcortex tareas.cortex
```

```markdown
<!-- HCORTEX v=1.0 t=canonical k=corpus -->

<!-- glossary -->
$0:KERNEL
$0:format{cortex:1.0,encoding:UTF-8,language:es}
$0:enum_state{values:"pendiente|hecho"}
TAR:task{type:attrs,weight:M,focus:desc,desc:"Tarea simple",fields:"desc:text|estado:%state"}

<!-- /glossary -->

## §1: TAREAS

<!-- schema:1 capa:DATA -->
### TAR:comprar
| desc | estado |
|---|---|
| "Comprar pan" | pendiente |

### TAR:llamar
| desc | estado |
|---|---|
| "Llamar al medico" | hecho |

<!-- /schema:1 -->
```

Y de vuelta a máquina:

```bash
python -m codec_cortex from-hcortex tareas.md   # compila y auto-valida
```

## Paso 5: verificá el viaje

```bash
python -m codec_cortex validate tareas.cortex     # exit 0 si es válido
python -m codec_cortex canonicalize tareas.cortex # forma canónica estable
python -m codec_cortex hash tareas.cortex         # firma del documento
python -m codec_cortex loss-report tareas.cortex  # qué información no sobrevive
```

`loss-report` responde la pregunta incómoda: **qué se pierde**. En este ejemplo
no hay pérdidas (`"losses": []`). Si agregás un comentario `#` o un espacio de
más, el reporte lo nombra con un código del catálogo cerrado.

## Errores que vas a ver

| Código | Significado | Arreglo |
|---|---|---|
| `G010_FORMAT_REQUIRED` | falta `$0:format` | declarar `cortex:1.0` |
| `G007_UNSUPPORTED_VERSION` | versión desconocida | usar `1.0` (o leer `0.1`/`0.2`) |
| `G042_GLOSSARY_HEADER_INVALID` | `$0: <título>` | usar `$0` o `$0:<CAPA>` |
| `I012_POSITIONAL_ARITY` | celdas ≠ contrato | ajustar celdas o el contrato |
| `U003_NON_ASCII_IDENTIFIER` | nombre/clave no ASCII | identificadores ASCII (el contenido sigue libre) |
| `H481_HIDDEN_COPY` | HCORTEX con copia oculta del AST | regenerar el render |
| `L402` / `L403` / `L405` | pérdidas declaradas | ver [`LOSS-REPORT.md`](LOSS-REPORT.md) |

## Siguientes pasos

| Documento | Contenido |
|---|---|
| [LOSS-REPORT.md](LOSS-REPORT.md) | catálogo de pérdidas y JSON del reporte |
| [MIGRATION-1.0.md](MIGRATION-1.0.md) | si venís de 0.1/0.2 |
| [standard/CORTEX-SPEC-1.0.md](standard/CORTEX-SPEC-1.0.md) | el canon completo |
| [parser-api.md](parser-api.md) | API Python y CLI de las cinco superficies |
| [../skill/codec-cortex.skill.md](../skill/codec-cortex.skill.md) | el estándar en CORTEX, para LLMs |
