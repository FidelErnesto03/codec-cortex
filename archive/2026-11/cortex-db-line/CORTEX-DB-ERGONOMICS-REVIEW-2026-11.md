# CORTEX-DB — Revisión de Ergonomía desde la Práctica del Equipo Agentico

> **Estado:** v0.1 — 2026-11-12. Complemento del Documento de Visión (§14).
> **Tarea:** T-008 (CYCLE-03, sesión SES003).
> **Autor:** Alfred (gobernador), a pedido expreso del Arquitecto: *"TÚ puedes establecer si la ergonomía usada es útil, fiable y escalable; TÚ, Heimdall, Jarvis y Seshat han estado trabajando y saben dónde está bien y dónde falta."*
> **Fuentes:** contratos de identidad y lecciones registradas de las cuatro personas (`.arqux/identities/*.cortex`), registro de issues de CODEC-CORTEX (U2–U12 y cerrados E-0211..E-0235), lecciones del brain, PULSE de sesiones SES001–SES003, y la experiencia directa de Alfred gobernando este proyecto (2026-07 → hoy).

---

## 0. Método y advertencia de sesgo

Los cuatro somos sujetos **y** instrumentos: fuimos entrenados con las correcciones del Arquitecto, así que nuestro entusiasmo no valida nada. Reglas aplicadas: (1) cada ítem lleva procedencia — persona, issue o lección registrada; (2) lo que es testimonio se marca como testimonio; (3) lo verificable se cita con su evidencia (evento PULSE, issue, commit o certificado). El veredicto final está diseñado para ser falsificable con los experimentos E5/E6 del anexo competitivo.

## 1. Dónde la práctica dice que está BIEN (conservar)

| # | Propiedad | Evidencia vivida | Procedencia |
|---|---|---|---|
| 1.1 | **Restauración determinista de contexto** — cualquier ejecución puede reanudar cualquier sesión desde el brain: foco, objetivos, lecciones, riesgos, estado de BLPs | SES003 pausada el 2026-11-03, reanudada el 2026-11-12: estado completo de BLP-004, backlog y cambios sin commit recuperados desde brain + checkpoint; sin conversar con nadie | Sesión SES003 (presente); patrón AXM:resume en uso desde CYCLE-01 |
| 1.2 | **Superficie handler-first auditada** — cada mutación deja evento PULSE trazable; el gobernar-sin-editar-archivos funciona | E-0264/E-0265/E-0267/E-0268 de hoy; ~270 eventos en el brain de este proyecto | PULSE SES001–SES003 |
| 1.3 | **Selección sin distorsión** — perfiles P0–P2 que omiten secciones por regla (compresión = selección, no paráfrasis); HCORTEX legible para humanos | Lectura de brain con perfil WORK omitiendo entradas P3 de forma determinística | cortex.read hoy; mecanismo de perfiles del códec |
| 1.4 | **Cultura de certificación** — corpus + vectores + certificador con hash de instrumento, firma de auditor independiente, cadena audit.sig 1.1→1.2→1.3 | D1 141/141, D3b 101/101 en 5 superficies, SIGNED-PASS de Heimdall sobre commits verificados | BLP-006/007/008, bench/certify.py |
| 1.5 | **Separación de roles como constitución en contexto** — el ejecutor no crea gobierno, el auditor no muta, el gobernador decide; la auditoría adversarial es un rol del workflow, no un plugin | Contratos de Jarvis (LIM:no_create), Heimdall (LIM:no_mutation, read-only), Seshat (LIM:no_auto_publish) | Identidades del workspace |
| 1.6 | **Trazabilidad total por defecto** — issues con transiciones PULSE, timelog por sesión, evidence con taxonomía (note/artifact/decision/metric/blocker) | 6 issues de usabilidad abiertos con estados transicionados; timelog SES003 vivo | Registro de issues; timelog |

## 2. Dónde la práctica dice que DUELE (corregir — con procedencia)

| # | Fricción | Procedencia | Lección para CORTEX-DB |
|---|---|---|---|
| 2.1 | **La rampa de escritura exige reglas tácitas** (~10): sección, sigilo, unicidad de nombre, formato de attrs sin llaves (las llaves se rechazan), level metadata, dialecto del archivo. Se aprenden con cicatrices | Lección registrada de Alfred (formato unbraced); este flujo de trabajo diario | El modelo declarado (dialecto+perfil+arquetipo) debe absorber las reglas; la escritura canónica no debe conocerlas el usuario |
| 2.2 | **Meta-handlers asimétricos / el dry-run miente**: cortex_patch aprobó en dry-run lo que el apply real rechazó; blueprint.ac exige in_progress pero blueprint.update enmienda done; métricas de entry.add vs entry.update difieren | Lección registrada (confianza 0.6): "el dry-run de patch miente"; asimetrías documentadas en lecciones ArqUX | Una sola implementación de semántica por operación; dry-run ejecuta el mismo camino de validación |
| 2.3 | **Éxitos silenciosos**: checkpoints vacíos grabados como ok (E-0108..E-0113 con fcs/obj vacíos; deuda "checkpoint vacío" heredada a ArqUX); duplicados de sigilo silenciosos en 0.1 (E-0215); from_hcortex emitía fuente inválida sin validar (E-0235) | Brain PULSE; issues cerrados | Nada en silencio: escribir vacío o inválido es error con diagnóstico, no un ok que se descubre meses después |
| 2.4 | **Servidor stale y caches de arranque**: editar handlers no tiene efecto hasta reiniciar; un identity.record sobre servidor stale reprodujo en vivo el bug E-1808 (GSIG 4→0, LNG inyectado en contrato level-1) | Lección registrada (confianza 0.7) con incidente E-1808 | Semántica de hot-reload y API versionada son requisitos ergonómicos, no lujos |
| 2.5 | **Ciclo de vida de sesión/identidad con muros**: SESSION_OPEN_EXISTS bloquea y obliga a ritual de reanudar/cerrar (recuperable, pero es una pared para recién llegados); identity_switch falla desde la raíz del workspace; handoff+switch son dos llamadas acopladas que siempre van juntas | Hoy mismo (SESSION_OPEN_EXISTS al abrir sesión); lección registrada sobre rutas de identity_switch; pares handoff/switch repetidos en PULSE (E-0163/E-0164, E-0177/E-0178, E-0198/E-0199…) | El ciclo de vida debe ser un asistente, no una secuencia que hay que saberse; la base expone "reanudar o cerrar" como decisión guiada |
| 2.6 | **No existe consulta transversal**: los selectores direccionan un archivo, no un corpus; para "todas las lecciones de todos los brains" el único camino realista es grep — que el marco prohíbe para gobernanza | Brecha vivida por Alfred en cada sesión multi-proyecto; el handler `cortex.learn` escanea, pero no es consulta | El lenguaje de consulta de la base (catálogo + filtros + temporal) es el desbloqueo ergonómico interno más importante |
| 2.7 | **Crecimiento sin control del brain**: 90 KB, PULSE que exige compactación manual (pulse.compact con pruned=99 en una sesión), gc de duplicados como operación separada | Brain de CODEC-CORTEX hoy; E-0101 (pruned=99), E-0102 (gc dedupe) | Retención y compactación como política del motor, no como tarea manual del gobernador |
| 2.8 | **Contratos de CLI divergentes entre superficies**: Node prefija digests con `sha256:`, Bash hashea el archivo crudo, el binario Go quedó stale frente al release (E-0211), los fixes de Python tuvieron que portarse a 4 superficies (E-0224) | Lección de tooling (confianza 0.6); issues E-0211/E-0224 cerrados | Un contrato canónico único de CLI (mismos comandos, mismos flags, mismas salidas) es requisito de la base multi-runtime |
| 2.9 | **Validador centrado en brains**: plantillas de identidad (que no son brains) exigían FCS para pasar E024; la migración reescribe formato pero no repara contenido (E032 en 6/7 identidades post-migración) | Lecciones de Jarvis (BLP-042): "los templates de identidad necesitan FCS para pasar E024"; "migrate_cortex_file() no repara errores de contenido" | La validación valida contra el arquetipo declarado — nunca asume que todo documento es un brain; migrar y validar/repair son un paso |
| 2.10 | **Gates que disparan tarde y protección lógica distribuida**: blueprint.ready devolvió LEARNING_NOT_RECORDED después de aprobar 6 gates (BLP-015); la semántica de survive está implementada en 5 capas (document_kind, validator, perfiles, scoring, tests legacy) | Lecciones de Jarvis (BLP-015, T-1.1) | Gates pre-chequeables en una llamada; invariantes con única fuente de verdad |
| 2.11 | **Errores hablan en códigos, no en humanos**: G007, E024, E032 sin sugerencias; did-you-mean y diff semántico siguen abiertos como backlog | Issues abiertos U8/U5 (diagnósticos did-you-mean) y U9/U12 (cortex-diff semántico, verify de mayor fidelidad) | La base nace con diagnósticos que proponen la reparación (cierra U8/U5/U9/U12 en su diseño, no como backlog) |
| 2.12 | **Backlog de usabilidad del códec todavía abierto**: fachada de API de dominio con docstrings mínimos (U2/U3), helper de emisión ideática escapado sin sanear (U4, severidad alta), check por stdin (U10), comentarios libres condicionales (U7) | Issues abiertos del 2026-11-03 (revisión NEX cap. 3) | La fachada de la base hereda estas deudas; resolverlas antes de F2 o declararlas no-objetivo de la base |

## 3. Brechas de evidencia (lo que hoy no sabemos)

- **Fidelidad a nivel de conducta** (¿el agente sostiene axiomas tras compresión mejor que con resúmenes?): testimonio fuerte + mecánica demostrable, medición pendiente → E5.
- **Ventaja de determinismo sobre similitud en números**: no hay medición comparada → E6.
- **Ergonomía percibida por un externo**: todo nuestro registro es de nativos del marco; no hay usuario ingenuo medido. El primer tester externo de F2/F3 debe medirse contra el protocolo "2 llamadas" del mercado.

## 4. Veredicto (mi visión, falsificable)

**¿Es útil?** Sí — con la evidencia más fuerte que tenemos: el trabajo agentico de este workspace se sostiene hace meses sobre este sustrato (20 proyectos gobernados, 4 personas, sesiones reanudadas semanas después, 24 BLPs en este proyecto solo). Nada de eso existiría sin restauración determinista + trazabilidad.

**¿Es fiable?** En el núcleo, sí: canonicalización, hash, roundtrip y certificación son la parte más sólida y verificada. En la periferia, no todavía: la fiabilidad real depende de disciplina manual (checkpoints buenos, compactaciones a tiempo, servidor fresco) — y esa dependencia es la que generó nuestros trastropiezos (2.3, 2.4, 2.7).

**¿Es escalable?** Para equipos como el nuestro — con kernel (AGENTS.md), handlers y roles — sí, y es demostrable. Para el mercado, no en su estado actual: la rampa (2.1), la ausencia de consulta transversal (2.6) y los contratos divergentes (2.8) son las tres paredes. La base las derrumba si y solo si adopta la doctrina de §5.

**Comparado con el mercado:** en la barra de *rampa* perdemos contra Mem0 (2 llamadas) — y no deberíamos intentar ganarla imitándolo. En la barra de *confianza* ganamos sola: restauración verificable, tamper-evidence, esquema versionado, conformance multi-runtime y auditor adversarial incorporado son cosas que ningún líder ofrece hoy. El objetivo ergonómico correcto no es "tan simple como mem0.add" sino **"dos llamadas gobernadas"**: tan pocas como ellos, con garantías que ellos no dan.

## 5. Doctrina ergonómica para CORTEX-DB (mi propuesta, 10 puntos)

1. **Declarar una vez, escribir en dos llamadas.** El modelo (dialecto+perfil+arquetipo) absorbe las reglas tácitas (2.1); la superficie diaria se reduce a `context.load` y `memory.write`.
2. **Fallar en voz alta.** Ningún éxito silencioso: checkpoint vacío, duplicado o entrada inválida es error con diagnóstico (2.3).
3. **Errores que proponen la reparación.** did-you-mean, diff semántico y sugerencia de fix nativos del motor (2.11).
4. **Un contrato de CLI canónico** en todos los runtimes: mismos comandos, flags y salidas (2.8).
5. **Migrar = validar + plan de reparación en un paso** (2.9).
6. **Gates visibles y pre-chequeables** — nada que apruebe 6 y dispare en el 7.º (2.10).
7. **Selectores deterministas + índice vectorial derivado y firmado** para descubrimiento (2.6; síntesis §14 de la visión).
8. **Hot-reload y API versionada** — el motor que cambia bajo el agente no puede envenenar escrituras (2.4).
9. **Crypto-shredding desde el día uno** — el journal inmutable convive con el derecho al olvido por diseño.
10. **Sigilos nativos + alias en inglés curados** — la nomenclatura de adopción sin renunciar al vocabulario interno (decisión del Arquitecto sobre roles ya apunta ahí).

## 6. Ligazón con los experimentos

La doctrina se falsifica con los mismos experimentos del anexo competitivo: E5 (fidelidad maratónica) valida §4-fiable a nivel de conducta; E6 (determinismo vs vectorial) valida la propiedad de dirección determinista; y la medición con un tester externo ingenuo en F2/F3 valida la rampa de §4-escalable.

---

*Testimonios marcados como tales; cada ítem de fricción cita su issue, lección o evento. Nada aquí es promesa: es el registro de donde estamos parados.*
