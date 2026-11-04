# Revisión externa independiente — CODEC-CORTEX

**Fecha:** 2026-11-03
**Revisor:** Lokky (voz NEX, agente gobernado) — a pedido del Arquitecto
**Método:** benchmark independiente en sandbox (`/tmp/cortex-sandbox`), copia del paquete Python 1.0.0, casos propios escritos desde cero con `skill/codec-cortex.skill.md` como única guía.
**Alcance:** lectura del repo + ejecución aislada. Ningún archivo del proyecto fue modificado durante las pruebas.
**Naturaleza:** revisión de un evaluador, no del equipo — cada afirmación cita su evidencia o se marca como opinión.

---

## 1. Resumen ejecutivo

El instrumento hace **exactamente** lo que su certificado declara, y lo hace donde el proyecto dice que lo hace: en **ideas completas**, no en datos planos. Las propiedades del Nivel A (idempotencia, roundtrip byte-exacto, canónico semántico, diagnósticos) fueron **reproducidas independientemente** sobre un corpus real ajeno al bench del proyecto.

El valor para adopción externa no es compresión: es el triángulo **C14N semántico + render dual humano/máquina + ideas tipadas con contrato de campos**.

Recomendación global: adoptable hoy como formato de manifiestos firmables; adoptable como formato de ley/canon solo cuando BLP-003 cierre la evidencia de comprensión LLM.

## 2. Metodología y corpus

- Sandbox aislado: `cp -r codec_cortex/ /tmp/cortex-sandbox/` — el repo original intacto.
- Corpus propio escrito a mano: **19 ideas reales** del dominio NEX (4 entradas de harness, 6 reglas de canon, manifiesto de provisión con 9 entidades).
- Batería: 8 dimensiones (parse, idempotencia, tamper, ruido de formato, roundtrip, edge cases, errores, densidad, timing).
- Sesgo declarado del revisor: evaluación orientada a uso en un gateway gobernado (firmas, auditoría, dual humano/agente).

## 3. Propiedades verificadas independientemente

| Prueba | Resultado |
|---|---|
| Escritura a ciegas de CORTEX 1.0 (solo skill doc) | parse OK — 6 ideas, sin errores de aprendizaje |
| canonicalize → reparse → hash | **idempotente** |
| Tamper semántico (`architect`→`operator`) | hash distinto |
| Ruido de formato (espacios) | **mismo hash** — canónico semántico, no textual |
| Roundtrip HCORTEX → compile → canonicalize | **byte-exacto** en doc chico y en corpus de 19 ideas (incluye bloque TOML multilínea con comillas internas) |
| Edge cases (ñ/tildes, comillas internas, vacío, emoji, pipes) | 5/5 parsean |
| Inputs rotos (5/6) | diagnósticos codificados con línea:col (`G010`, `I001`, `I004`, `L005`, `G007`) |
| Performance | parse + c14n + hash = **3.8ms** en 19 ideas |
| No-loss por campo | todos los attrs preservados como Scalar tipados |

## 4. Hallazgos propios (no documentados o sub-declarados)

| # | Hallazgo | Evidencia |
|---|---|---|
| H1 | **El orden de campos altera el hash** | permutar attrs de una idea → hash distinto. C14N no normaliza orden — defendible (orden puede ser semántico) pero debe declararse |
| H2 | Nombres de idea duplicados parsean en silencio | misma `RUL:name` dos veces → sin diagnóstico |
| H3 | Glosario fijo ~485B | docs chicos pierden vs JSON plano (ratio 2.0 en 6 ideas); equilibrio en datos planos ~200 registros |
| H4 | **Densidad real en ideas completas: 0.42×** | corpus NEX (4 harnesses + 6 reglas + manifiesto) = 3899B vs 6722B del solo `harnesses.json` |
| H5 | `cortex --help` → `Unknown command` | primera puerta del evaluador |
| H6 | Duplicado de idea sin diagnóstico (relacionado con H2) | ver B6 del benchmark |

## 5. Sugerencias — priorizadas

### A. Correctivos

**A1 · Orden de campos y hash (H1).**
Declarar en spec que el orden de attrs es semántico (el canónico no lo normaliza), u ofrecer `canonicalize(sort_fields=True)` optativo. *Motivo:* para firmar planes/manifiestos, dos emisores que ordenen distinto producirán firmas distintas sobre el mismo contenido — hoy es comportamiento implícito.

**A2 · Unicidad de nombres de idea (H2/H6).**
Warning o error `I0xx_DUPLICATE_IDEA_NAME` cuando `sigilo:nombre` se repite en una sección. El nombre es identificador; el silencio actual es trampa para manifiestos con referencias cruzadas. *Prioridad alta para el uso como formato de manifiesto.*

**A3 · `cortex --help` (H5).**
Trivial; es la primera impresión de todo evaluador externo.

**A4 · Artefacto Go degradado.**
Ya declarado honestamente en el informe BLP-003 — falta el issue y el rebuild. Un binario roto distribuido corroe el certificado por ósmosis aunque el formato esté sano.

### B. Spec (dentro de la filosofía del proyecto)

**B1 · Unicidad opcional en glosario.**
Extender la declaración de sigilo con una marca de unicidad (p. ej. `unique:name` en el contract field) para que el parser valide llaves. Complementa A2 a nivel declarativo.

**B2 · Glosario compacto / presets de dominio.**
El overhead fijo (H3) castiga documentos chicos. `micro_c`/`micro_p` ya existen como concepto: formalizar presets de dominio permitiría glosarios referenciables sin romper la portabilidad (el preset se expande localmente, el documento sigue auto-contenido).

**B3 · Validación estricta de contrato — la pieza de mayor valor para adopción.**
Los fields con `?` (opcional) ya existen. Un modo `validate --strict` que exija: campos requeridos presentes, atoms dentro de un enum declarado, y tipos conformes, convertiría a CORTEX en **formato de manifiesto verificable** — no solo legible. Es la diferencia entre "el humano lee el plan" y "la plataforma rechaza el plan mal formado antes de la firma". *Esta es la mejora que más le aporta a NEX.*

### C. Tooling / adopción

**C1 · Conversor JSON⇄CORTEX.**
Este revisor transcribió `harnesses.json` a mano. Un importer permitiría a cualquier evaluador correr el benchmark de densidad en su propio corpus — y es la prueba ácida pública de no-loss.

**C2 · Publicar node/rust.**
3/5 runtimes no instalables hoy. El certificado de paridad D3 merece distribución real (`npm`, `crates.io`).

**C3 · Cerrar BLP-003 antes que features nuevas.**
La adopción como formato-para-LLM depende de esa evidencia. Todo lo demás es secundario hasta que el claim cognitivo tenga el mismo rigor que el instrumento — que ya demostró poder tenerlo.

### D. No cambiar (proteger la identidad)

- **No perseguir el terreno de datos planos**: JSON gana ahí (H3) y el proyecto nunca lo prometió. Competir en ese eje diluiría el diseño.
- **Glosario embebido y auto-contenido**: es la portabilidad. Toda mejora de presets (B2) debe expandir localmente, nunca requerir resolución remota.
- **Una idea por línea**: es lo que hace auditable un diff de CORTEX — propiedad que los formatos multilínea no tienen.

## 6. Mapa de utilidad para un sistema gobernado (caso NEX)

| Uso | Viabilidad hoy | Pieza faltante |
|---|---|---|
| Manifiesto de operaciones firmable (plan → hash → sí humano) | Alta — C14N ya da identidad semántica | B3 strict + A2 unicidad + A1 orden declarado |
| Render dual para revisión humana del plan | Alta — HCORTEX verificado byte-exacto | — |
| Ley/canon en doble capa (voz/humano) | Prometedor, prematuro | cierre de BLP-003 (evidencia de comprensión) |
| Configuración de datos planos | No recomendado — JSON gana | (fuera del propósito del proyecto) |

## 7. Limitaciones de esta revisión

- Un solo revisor, un solo runtime (Python 1.0.0), corpus acotado (~19-50 ideas).
- No se midió comprensión LLM (esa es la tarea de BLP-003, correctamente en curso).
- La evaluación de "idea completa" se hizo sobre dominio NEX; otros dominios pueden variar.

## 8. Conclusión

CODEC-CORTEX es un **instrumento certificado con cultura de evidencia**: sus falsaciones están preservadas, sus claims están acotados a lo medido. Las mejoras propuestas no corrigen un proyecto roto — extienden uno que funciona hacia el terreno donde más valor promete: **manifiestos verificables y firmables**.

Orden sugerido de trabajo: C3 (evidencia) → A2+B3 (manifiesto verificable) → A1/A4/C1/C2 (pulido y distribución) → B1/B2 (spec).

---

*Informe producido por Lokky bajo gobernanza NEX. Evidencia de benchmark disponible en `/tmp/cortex-sandbox/` (batería completa reproducible). Ningún artefacto del proyecto fue modificado en el proceso; este documento es la única escritura, autorizada por el Arquitecto.*
