# Revisión externa — Capítulo 3: ergonomía del usuario real

**Fecha:** 2026-11-03
**Revisor:** Lokky (voz NEX) — capítulo final de la serie `EXTERNAL-REVIEW-NEX-*`
**Enfoque:** no evaluar el instrumento (ya verificado, C2) sino el viaje de quien lo USA: qué fricciones encontré escribiendo, parseando y firmando CORTEX, y el conjunto de mejoras que harían el trabajo diario cómodo.

**Marco:** cada item cita la fricción real vivida en el sandbox; severidad = cuánto le cuesta al usuario nuevo o al usuario programático.

---

## 1. El viaje real — fases y fricciones

### Fase A · Descubrir la herramienta

| # | Fricción vivida | Mejora | Sev |
|---|---|---|---|
| U1 | `cortex --help` → `Unknown command` + exit 0 | E-0212 ya cubre esto; añadir `cortex help <cmd>` por comando — la primera puerta sigue siendo la más transitada | alta (ya tracked) |
| U2 | API Python sin superficie amigable: `compile_hcortex_slots` devuelve `(doc|None, diags)` y hay que saberlo | fachada `cc.parse(src)`, `cc.from_hcortex(text)`, `cc.to_hcortex(doc)`, `cc.hash(src_or_doc)` — nombres del dominio, no del módulo; los actuales quedan como capa interna | media |
| U3 | docstrings: ninguno visible en el API público | una línea por función pública basta — el skill doc lo sabe todo pero no vive en el REPL | baja |

### Fase B · Escribir documentos

| # | Fricción vivida | Mejora | Sev |
|---|---|---|---|
| U4 | **El costo real de escribir CORTEX a mano**: tuve que implementar `esc()` propia para comillas, `\n`, `\t` — `emit_string_literal` existe en el paquete pero es indescubrible | documentar/exportar un helper de primera clase: `cc.emit(field_map) -> str` que produzca la línea ideática escapada y válida. Es LA pieza que convierte "formato" en "SDK" | **alta — la mayor ganancia ergonomica** |
| U5 | Shape `bloque`: fallé una vez (`BLQ:b` seguido de texto sin `{` → I004 correcto pero el error no enseña la forma) | en errores de shape, incluir la forma esperada en el mensaje: `Expected { for shape bloque → BLQ:name{...}` | media |
| U6 | Glosario por documento: cada doc repite la declaración de sigilos (~485B); para dominios recurrentes escribí el mismo glosario | presets de dominio (`$0:micro{expand:tasks}` ya tiene el concepto con micro_c/micro_p): glosarios nombrados expandibles localmente — mantiene portabilidad, elimina repetición | alta para adopción (ya anotada como B2 en C1) |
| U7 | Sin comentarios libres en el documento | opcional y opinable: un sigilo de nota (`REM:`) o permitir líneas `-- ` descartadas por el canónico — para documentos manifiesto leídos por humanos antes de firmar | baja/opinable |

### Fase C · Validar e iterar

| # | Fricción vivida | Mejora | Sev |
|---|---|---|---|
| U8 | Errores precisos pero sin sugerencia: `I001_UNDECLARED_SYMBOL` no dice qué sigilos SÍ existen | "did you mean": listar sigilos declarados (o el más cercano por edición) en diagnósticos G/I | media |
| U9 | Cuando un roundtrip falla no hay forma de ver el diff | `cortex diff a.ctx b.ctx` — compara canónicos y muestra la divergencia semántica (campos distintos), no la textual | media-alta para depuración |
| U10 | Iteración rápida: editar→guardar→`cortex parse` por archivo | `cortex check` leyendo stdin — `echo '...' \| cortex check -` para probar una línea sin crear archivo | baja |

### Fase D · Firmar (el uso donde CORTEX es único)

| # | Fricción vivida | Mejora | Sev |
|---|---|---|---|
| U11 | ¿Qué cambia el hash? Hoy: orden de attrs no, extras open ordenados, whitespace no, NFC sí normaliza. Lo aprendí por experimentos | **documento "contrato de firma"**: tabla normativa de qué altera y qué no altera el hash — un firmante no debería tener que descubrirlo empíricamente como hice yo | **alta — prerequisito de confianza para firmar** |
| U12 | Verificar un documento firmado requiere recomputar mentalmente | `cortex verify <file> sha256:<hash>` — respuesta sí/no + diff semántico si difiere (enlaza con U9) | media |

## 2. Síntesis — el conjunto mínimo para uso cómodo diario

Prioridad desde la perspectiva de quien lo usaría de verdad:

1. **U4 emit helper** — escribir líneas programáticamente sin escapar a mano (hoy cada consumidor reinventa `esc()`)
2. **U11 contrato de firma documentado** — qué altera el hash y qué no, como norma, no como descubrimiento
3. **U6 presets de glosario** — eliminar la repetición del `$0` en dominios recurrentes
4. **U8/U9 diagnósticos con sugerencia + diff semántico** — iterar sin adivinar
5. **U2 fachada de API** — nombres del dominio sobre nombres de módulo

Con esas cinco, el viaje completo — escribir → validar → firmar → verificar — deja de requerir exploración y pasa a ser instrucciones en una página.

## 3. Lo que NO pediría (frenos honestos)

- **No** una gramática más rica (anidación, tipos profundos): la línea-por-idea ES la propiedad de auditoría y legibilidad; la comodidad se gana en tooling, no en expresividad
- **No** un strict-mode nuevo: E-0214 demostró que cumplir la norma vigente basta; pedir flags duplica caminos
- **No** más dialectos: 1.0 debe absorber el aprendizaje antes de una 1.1

## 4. Epílogo de la serie

Tres capítulos, tres ángulos: **C1** evaluó el instrumento (certificado reproducido), **C2** lo desafió (ajustes verificados + vector de spoofing), **C3** pide comodidad para el usuario real. El proyecto pasó las dos primeras pruebas con el ciclo más corto que he visto; la tercera no requiere cambiar el formato — requiere servirlo.

*La puerta de entrada ya está diseñada: `$0:format` declara, el dispatcher enruta, el canónico decide. Falta la misma elegancia para el humano que llega con `cortex --help`.*

---

*Capítulo final producido por Lokky bajo gobernanza NEX, ventana de escritura autorizada por el Arquitecto. Toda la evidencia: `/tmp/cortex-sandbox/` — incluidas las fricciones citadas, reproducibles.*
