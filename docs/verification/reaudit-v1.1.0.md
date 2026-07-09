Perfil: CORTEX-FULL
Modo: HCORTEX-AUDIT
Documento: CODEC-CORTEX CLI v1.1.0 — Re-auditoría técnica post-entrega
Fecha: 2026-06-26
Objeto auditado: /mnt/data/codec-cortex-1.1.0.tar.gz
Informe auditado: /mnt/data/INFORME_DE_ENTREGA.md
Spec de referencia disponible en conversación: /mnt/data/SKILL.md

# 1. Resultado ejecutivo

## Veredicto

La versión `codec-cortex` v1.1.0 representa una mejora sustancial frente a la v1.0.0. El aplicativo ya no debe considerarse un subconjunto permisivo simple: contiene hardening real del validador, perfiles HCORTEX, recovery, comandos de diagrama, aliases canónicos y documentación de madurez.

Sin embargo, no puedo validar como cierta la afirmación “todas las brechas quedaron cerradas” sin reservas. La re-auditoría detectó fallas concretas en la correspondencia entre claims, tests y comportamiento real del CLI.

Dictamen técnico:

```text
Estado real: v1.1.0 es un avance fuerte y funcional.
Conformidad SKILL: parcial-alta, pero no plena.
Riesgo principal: claims de cierre total con gates insuficientemente adversariales.
Acción recomendada: v1.1.1 de hardening, no rediseño.
```

## Resultado de ejecución reproducida

| Prueba | Resultado |
|---|---:|
| Extracción segura del tarball | OK |
| Suite oficial `python -m pytest src/tests/ -q` | 88/88 pasan |
| CLI `python -m cortex --version` | cortex 1.1.0 |
| Comandos declarados en help | Presentes |
| Revisión estática de módulos críticos | Completada |
| Pruebas adversariales adicionales | 7 hallazgos relevantes |

# 2. Correspondencia positiva con SKILL.md

## 2.1 Mejoras reales incorporadas

La v1.1.0 sí incorpora piezas que responden directamente a la auditoría anterior:

| Área | Evidencia observada | Juicio |
|---|---|---|
| Parser / AST / writer | `src/cortex/core/parser.py`, `ast.py`, `writer.py` | Base sólida |
| Validación cognitiva | `src/cortex/core/document_kind.py`, `validate_level_policy()` | Mejora importante |
| FCS/OBJ en brain | `E024_LEVEL2_MISSING_FOCUS` | Implementado en API interna |
| Separación Nivel 1/2/3 | `E023_LEVEL1_LIVE_STATE`, `E029_LEVEL3_LIVE_STATE` | Parcialmente implementado |
| `survive` | `E025_INVALID_SURVIVE` | Implementado |
| `CNST:blocking → survive:min` | `E026_BLOCKING_NOT_P0` | Implementado |
| Secretos en claro | `E028_SECRET_IN_CLEAR` | Implementado de forma heurística |
| HCORTEX perfiles | `src/cortex/hcortex/profiles.py` | Implementado |
| HCORTEX-AUDIT | `--mode audit` con columna `source` | Implementado |
| Recovery | `cortex recover` | Implementado |
| Diagramas | `cortex diagram list/extract/validate` | Implementado, con salvedad de verbatim |
| Aliases canónicos | `decode`, `encode`, `patch_add`, `patch_update`, `patch_remove` | Presentes |
| Documentación madurez | `STATUS.md`, `BENCHMARK.md`, `README.md` | Presente, pero con inconsistencias |

## 2.2 Correspondencia conceptual

La herramienta avanza hacia el modelo correcto:

```text
.cortex → AST → validación → render HCORTEX / edición / roundtrip
```

También empieza a trasladar la especificación desde disciplina manual hacia verificación automatizada. Eso es exactamente el camino correcto para CODEC-CORTEX.

# 3. Hallazgos críticos de re-auditoría

## H-RA-01 — `--kind` existe, pero no gobierna la validación real

### Evidencia

En `src/cortex/cli/commands/verify.py`:

```python
kind = None
if getattr(args, "kind", None):
    from ...core.document_kind import DocumentKind
    kind = DocumentKind(kind=args.kind, source="cli")

strict = getattr(args, "strict", False)
diagnostics = validate(doc, strict=strict)
```

El `kind` explícito se crea, pero no se pasa a `validate()`. Luego se usa para display. El mismo patrón existe en `doctor.py`.

### Prueba adversarial ejecutada

Archivo con `IDN:agent`, `FCS`, `OBJ`, `WRK`, validado como paquete:

```bash
PYTHONPATH=src python -m cortex verify /tmp/idn_agent_live.cortex --strict --kind package
```

Salida observada:

```text
kind:          package (inferred via cli)
errors:        0
rc=0
```

Pero la validación directa con `validate_level_policy(doc, DocumentKind("package","manual"))` produce:

```text
E029_LEVEL3_LIVE_STATE para FCS
E029_LEVEL3_LIVE_STATE para OBJ
E029_LEVEL3_LIVE_STATE para WRK
```

### Impacto

Este hallazgo debilita los claims:

- `verify --kind brain|skill|package|generic`
- `doctor --kind <kind>`
- gates CLI orientados a separación de niveles

### Severidad

Alta.

### Corrección requerida

Modificar `validate()` para aceptar `kind` opcional, o crear `validate_with_kind()`.

Propuesta mínima:

```python
def validate(doc: CortexDocument, strict: bool = False, kind: DocumentKind | None = None):
    ...
    findings.extend(validate_level_policy(doc, kind))
```

Y en CLI:

```python
diagnostics = validate(doc, strict=strict, kind=kind)
```

Agregar tests end-to-end CLI, no solo tests directos sobre API interna:

```text
test_cli_verify_kind_package_overrides_idn_agent
test_cli_doctor_kind_skill_overrides_filename_or_idn
test_cli_verify_kind_generic_disables_level_policy
```

---

## H-RA-02 — G2 declara `SES/LNG` vivos en SKILL, pero no los prueba ni los bloquea realmente

### Evidencia

El informe de entrega afirma que G2 valida que `SKILL.cortex` falla con `WRK/NXT/SES/LNG` vivo. En el código, la lista efectiva es:

```python
LIVE_STATE_SIGILS = frozenset({"FCS", "OBJ", "WRK", "STP", "NXT"})
```

No incluye `SES` ni `LNG`.

### Prueba adversarial ejecutada

Archivo `SKILL.cortex` con `$0` extendido que declara `SES` y `LNG`, más entradas activas:

```text
IDN:skill{name:"skill", status:"specification"}
SES:live{input:"x", output:"y", outcome:"z", date:"2026-06-26"}
LNG:live{type:"error", cause:"x", lesson:"y", prevention:"z"}
```

Comando:

```bash
PYTHONPATH=src python -m cortex verify /tmp/skill_with_ses_lng.cortex --strict --kind skill
```

Resultado:

```text
errors: 0
rc=0
```

### Impacto

El gate G2 no cubre lo que declara. Además, el SKILL establece que `SKILL.cortex` no debe contener estado vivo de sesión; `SES/LNG` pertenecen al cerebro operativo o a paquetes históricos, no al Nivel 1 como estado vivo.

### Severidad

Alta/media, según política final sobre `SES/LNG` en Nivel 1.

### Corrección requerida

Separar dos conjuntos:

```python
LIVE_WORKING_SIGILS = {"FCS", "OBJ", "WRK", "STP", "NXT"}
LIVE_SESSION_SIGILS = {"SES", "LNG"}
SKILL_FORBIDDEN_LIVE_SIGILS = LIVE_WORKING_SIGILS | LIVE_SESSION_SIGILS
```

Permitir `SES/LNG` solo si están marcados explícitamente como:

```text
nature:example | nature:template | nature:non_operational | nature:contract
status:specification
```

Y agregar tests reales:

```text
test_g2_strict_skill_with_live_ses_fails
test_g2_strict_skill_with_live_lng_fails
test_g2_strict_skill_with_historical_ses_example_passes
```

---

## H-RA-03 — HCORTEX no ordena globalmente P0→P5; agrupa por sección y puede mostrar P2 antes de P0

### Evidencia

`render_hcortex_read()` filtra y clasifica por P-level, pero luego renderiza las secciones en orden original:

```python
for sec in doc.sections:
    if sec.id == "$0":
        continue
    if sec.id not in sections_kept:
        continue
    ...
```

En un `brain.cortex` nuevo, la salida `render --mode readable --profile work` muestra primero `$1 · IDENTITY`, con `IDN`/`DOM` clasificados como P2, y luego `$2 · ACTIVE WORK`, con `FCS`, `OBJ`, `STP` clasificados como P0.

Salida observada:

```text
## $1 · IDENTITY
### Identity: agent <sub>[P2]</sub>
...
## $2 · ACTIVE WORK
### Focus: primary <sub>[P0]</sub>
```

### Impacto

El SKILL exige ordenar P0→P5 en render HCORTEX. La implementación actual aplica el filtro por P-level, pero preserva la arquitectura visual por secciones antes que el orden global de supervivencia cognitiva.

Esto no rompe lectura humana, pero sí rompe el claim fuerte de orden P0→P5.

### Severidad

Media.

### Corrección requerida

Definir explícitamente uno de estos dos modos:

1. `--layout priority`: render global P0→P5, recomendado para recovery/audit.
2. `--layout section`: render por secciones con badges P-level, recomendado para lectura humana.

Por defecto, `RECOVERY` y `MIN` deberían usar `priority`.

---

## H-RA-04 — `DIAG extract` no preserva verbatim: agrega newline final

### Evidencia

En `src/cortex/cli/commands/diagram.py`:

```python
f.write(text + "\n")
```

y en stdout:

```python
sys.stdout.write(text + "\n")
```

### Prueba adversarial ejecutada

Entrada DIAG sin newline final:

```text
DIAG:flow{@startuml
A-->B
@enduml}
```

Valor AST:

```python
'@startuml\nA-->B\n@enduml'
```

Archivo extraído:

```python
'@startuml\nA-->B\n@enduml\n'
```

Resultado:

```text
equal? False
```

### Impacto

El informe afirma que `diagram extract` preserva bloque DIAG verbatim. La función preserva contenido visual práctico, pero no preserva bytes exactamente.

### Severidad

Media.

### Corrección requerida

Para `--out`, escribir exactamente:

```python
f.write(text)
```

Para stdout, decidir si se prefiere UX o verbatim. Recomendación:

```text
stdout: text exacto por defecto
--print-newline: agrega newline para consola
```

Agregar test CLI real:

```text
test_g7_diagram_extract_out_preserves_exact_bytes
```

---

## H-RA-05 — `attrs-pos` no soporta `|` dentro de valores aunque estén entre comillas

### Evidencia

`parse_attrs_pos_body()` divide con:

```python
parts = [p.strip() for p in body.split("|")]
```

Esto no respeta comillas ni escapes.

### Prueba adversarial ejecutada

Entrada construida por el writer:

```text
HDL:decode{"decode | render" | "current" | ".cortex"}
```

Parseo observado:

```python
{'operation': '"decode', 'status': 'render"', 'requires': 'current'}
```

Validación:

```text
W002_INVALID_STATUS convertido a error en strict
E027_ATTRS_POS_ARITY
```

Roundtrip:

```text
roundtrip equal? False
```

### Impacto

El informe dice que el roundtrip estructural fue verificado con pipes, unicode, PlantUML y attrs-pos. Eso es cierto si se interpretan como casos separados. No es cierto para la combinación `attrs-pos + pipe dentro de valor`.

### Severidad

Media.

### Corrección requerida

Opción A — endurecida:

```text
attrs-pos prohíbe `|` dentro de valores aunque estén entre comillas.
El writer debe rechazar valores con `|` o degradar a attrs.
```

Opción B — robusta:

```text
implementar splitter quote-aware y escape-aware para attrs-pos.
```

La opción A es más coherente con máxima compresión y contrato estable.

---

## H-RA-06 — CRUD permite escribir entradas con sigilos no declarados

### Evidencia

`add_entry()` resuelve tipo así:

```python
sigil_def = doc.glossary.sigils.get(sigil)
type_ = sigil_def.type if sigil_def else "attrs"
```

No bloquea el alta si el sigilo no existe en `$0`.

### Prueba adversarial ejecutada

```bash
cortex add /tmp/crud_unknown.cortex --section 2 --sigil BAD --name x --value 'a:"b"' --force
```

Resultado:

```text
add_rc=0
"ok": true
```

Luego:

```bash
cortex verify /tmp/crud_unknown.cortex --strict --kind brain
```

Resultado:

```text
errors: 2
verify_rc=1
```

### Impacto

El comando puede persistir un archivo inválido sin confirmación. Esto contradice la idea de CRUD gobernado.

### Severidad

Media.

### Corrección requerida

Agregar política de mutación:

```text
Por defecto: no persistir si el resultado no pasa validate(strict=False).
Con --strict-write: exigir validate(strict=True).
Con --allow-invalid: permitir escritura inválida explícita para recovery/debug.
```

También bloquear sigilos desconocidos salvo:

```text
--create-sigil
--allow-unknown-sigil
```

---

## H-RA-07 — BENCHMARK.md contiene métricas `measured` con evidencia débil o contradictoria

### Evidencia observada

`STATUS.md` declara:

```text
Benchmark reproducible | planned | BENCHMARK.md define metodología; script pendiente
```

Pero `BENCHMARK.md` declara como `measured`:

```text
Parser throughput | measured | ~500–2000 archivos/s en CPU típica (estimado, no benchmark formal)
```

Esto mezcla `measured` con `estimado` y `no benchmark formal`.

También declara:

```text
Roundtrip structural fidelity | measured | 100% en fixtures controlados (61/61 tests)
```

pero la suite actual reporta 88 tests. Esto no es grave, pero sí desactualiza la evidencia.

### Impacto

El SKILL exige distinguir métricas medidas, target, hypothesis e illustrative. Aquí hay al menos un claim que debería ser degradado.

### Severidad

Media.

### Corrección requerida

Cambiar:

```text
Parser throughput: hypothesis o illustrative
```

hasta que exista script formal con:

```text
dataset
hardware
número de corridas
media
mediana
desviación estándar
intervalo de confianza
```

Corregir 61/61 → 88/88 o separar “criterios originales” de “suite total”.

---

## H-RA-08 — Inconsistencia de versión de SKILL canónica

### Evidencia

El informe de entrega declara:

```text
Spec canónica: SKILL.md v1.2.0-enterprise-candidate
```

Pero el `SKILL.md` disponible en esta conversación declara:

```text
SKILL.md · v1.1.0-enterprise-candidate
```

El README del paquete también menciona `SKILL.md v1.2.0-enterprise-candidate`.

### Impacto

No puedo afirmar correspondencia contra v1.2.0 si el canon entregado para esta auditoría es v1.1.0. Esto es un riesgo documental, no necesariamente funcional.

### Severidad

Media.

### Corrección requerida

Sincronizar:

```text
SKILL.md
README.md
STATUS.md
INFORME_DE_ENTREGA.md
pyproject metadata opcional
```

Y agregar test documental:

```text
test_declared_skill_version_matches_reference_file
```

---

## H-RA-09 — Artefactos declarados no están todos dentro del tarball auditado

### Evidencia

El informe lista:

```text
cortex_demo_v1_1.sh
CODEC_CORTEX_CLI_AUDIT_HCORTEX.md
SKILL_canon.md
INFORME_DE_ENTREGA.md
```

El tarball auditado contiene solamente el proyecto `cortex/`:

```text
README.md
BENCHMARK.md
pyproject.toml
CHANGELOG.md
STATUS.md
LICENSE
src/...
```

No hay `scripts/` ni `cortex_demo_v1_1.sh` dentro del paquete.

### Impacto

La suite Python sí es reproducible. La demo de 20 pasos declarada no fue verificable desde el tarball subido.

### Severidad

Baja/media.

### Corrección requerida

Incluir en el paquete:

```text
scripts/cortex_demo_v1_1.sh
SKILL_canon.md o referencia versionada
AUDIT_BASE.md si se usa como trazabilidad
```

O ajustar el informe: “artefactos entregados fuera del tarball”.

# 4. Brechas no críticas, pero importantes

## M-RA-01 — `validate()` no acepta `kind`, aunque `validate_level_policy()` sí

Esto es la causa raíz de H-RA-01. El diseño interno está cerca de ser correcto, pero la API pública central no expone la dimensión más importante de gobierno.

## M-RA-02 — `diff --profile governance --format json` siempre retorna 0

En `src/cortex/cli/commands/diff.py`:

```python
return 0 if (profile != "governance" and compare_ast(left, right).equal) else 0
```

Para JSON, siempre retorna 0. Esto es incorrecto para automatización CI.

## M-RA-03 — `recover` marca ambigüedad en diagnostics, no en RSK/AUD dentro del `.cortex`

El SKILL recomienda marcar ambigüedades como `RSK` o `AUD`. La implementación actual emite diagnostics (`E030`, `W010`) pero no inserta entradas `RSK` o `AUD` en el artefacto recuperado.

## M-RA-04 — `recover` puede asignar metadata canónica discutible por colisión de sigilos

Durante reconstrucción, `canonical_lookup` se llena con:

```python
brain_sigils() + skill_sigils() + package_sigils()
```

Las definiciones posteriores pisan anteriores. En una prueba con `IDN:agent`, el `$0` recuperado emitió:

```text
IDN | identity | attrs | B | Semantic | Package identity
```

Eso es semánticamente pobre para `IDN:agent`.

## M-RA-05 — Los tests G8 no garantizan realmente calidad de benchmark

El test solo exige que exista un bloque bash o la palabra pytest. No valida que cada métrica `measured` tenga evidencia individual, comando específico y dataset.

# 5. Evaluación de cierre de brechas del informe

| Brecha del informe | Estado real re-auditado | Juicio |
|---|---|---|
| H-01 FCS/OBJ en brain | Implementado internamente | Casi cerrado; falta corregir `--kind` CLI |
| H-02 separación niveles | Parcial | No cubre SES/LNG; `--kind` no gobierna validate |
| H-03 HCORTEX perfiles/P0-P5 | Parcial | Filtra bien; orden global P0→P5 no se cumple |
| H-04 pipes HCORTEX-EDIT | Cerrado para attrs | No cerrado para attrs-pos con pipe |
| H-05 attrs-pos sobrantes | Cerrado para exceso simple | Falta splitter quote-aware o prohibición explícita |
| H-06 legacy recovery | Funcional | Falta RSK/AUD persistente y mejor metadata canónica |
| M-01 inyección sin advertencia | Parcial | Recovery diagnostica; parser normal sigue seeding silencioso |
| M-02 strict | Implementado | Pero depende de validate sin `kind` explícito |
| M-03 secretos | Implementado heurístico | Correcto como current con límite declarado |
| M-04 AUD automático | Correctamente declarado planned | OK |
| M-05 STATUS/BENCHMARK | Presentes | BENCHMARK necesita corrección de claims |
| M-06 README overclaim | Mejorado | Pero versiona SKILL v1.2.0 no entregado |
| B-010 diagram | Funcional | Extract no es bit-perfect |

# 6. Recomendación de implementación v1.1.1

## Prioridad 1 — Corregir el bug de `--kind`

Impacto máximo con cambio pequeño.

```text
validate(doc, strict=False, kind=None)
verify.py → validate(doc, strict=strict, kind=kind)
doctor.py → validate(doc, strict=strict, kind=kind)
```

## Prioridad 2 — Endurecer gates con pruebas CLI reales

Los gates actuales prueban demasiado la API interna. Agregar pruebas end-to-end:

```text
CLI verify --kind package debe fallar con FCS/OBJ/WRK vivos.
CLI verify --kind skill debe fallar con FCS/OBJ/WRK/STP/NXT/SES/LNG vivos.
CLI diagram extract --out debe preservar bytes exactos.
CLI add debe rechazar sigil desconocido por defecto.
CLI diff governance json debe retornar non-zero si hay findings.
```

## Prioridad 3 — Definir política formal para `attrs-pos` con delimitadores

Recomiendo prohibir `|` dentro de valores `attrs-pos`. Es más simple, más determinista y más coherente con “máxima compresión”. Si se necesita texto libre, usar `attrs`.

## Prioridad 4 — Separar layout HCORTEX

Agregar:

```text
--layout priority|section
```

Default recomendado:

```text
MIN/RECOVERY → priority
WORK/FULL readable → section
AUDIT → priority salvo --layout section
```

## Prioridad 5 — Corregir BENCHMARK.md

Reclasificar throughput y corregir 61/61 vs 88/88.

```text
Parser throughput → hypothesis/illustrative
Roundtrip suite → 88/88 o especificar “61 originales + 27 nuevos”
```

# 7. Dictamen final

## Decisión

No regresaría la implementación. Tampoco aceptaría el informe como 100% cerrado.

La versión v1.1.0 es una buena base para consolidar el CLI, pero necesita una v1.1.1 corta y quirúrgica antes de declararla “audit-gates fully closed”.

## Estado recomendado de madurez

| Capacidad | Estado recomendado |
|---|---|
| Parser / AST / writer | current |
| HCORTEX-EDIT reversible | current con límite attrs-pos delimitador |
| HCORTEX-READ perfiles | current/specification, no claim de orden global |
| HCORTEX-AUDIT | current básico |
| Validación cognitiva interna | current parcial |
| CLI `--kind` | blocked hasta fix |
| Recovery | current parcial |
| Diagram extract verbatim | blocked hasta fix newline |
| CRUD gobernado | specification/current parcial |
| Benchmark reproducible | planned/parcial, no plenamente measured |
| MCP/runtime/promote/decay | future/planned según STATUS |

## Frase honesta de aceptación

```text
codec-cortex v1.1.0 implementa un subconjunto avanzado y probado del CLI CODEC-CORTEX, con mejoras reales de gobierno cognitivo. No obstante, la re-auditoría detecta brechas de correspondencia entre claims y comportamiento CLI, especialmente en --kind, separación Nivel 1 con SES/LNG, orden HCORTEX P0→P5, verbatim DIAG y claims de benchmark. Recomendado: publicar v1.1.1 de hardening antes de declarar cierre total de auditoría.
```

# 8. Checklist v1.1.1 sugerido

- [ ] `validate()` acepta `kind` explícito.
- [ ] `verify --kind` y `doctor --kind` afectan validación real.
- [ ] G2 incluye `SES/LNG` vivos en SKILL con `$0` extendido.
- [ ] Política formal para `attrs-pos` con `|` en valores.
- [ ] `diagram extract --out` preserva bytes exactos.
- [ ] `diff --profile governance --format json` retorna código correcto.
- [ ] `add/update/move/delete` ofrecen `--validate-before-write` o lo aplican por defecto.
- [ ] `recover` inserta `AUD`/`RSK` opcional en salida o declara que solo emite diagnostics.
- [ ] BENCHMARK.md reclasifica throughput.
- [ ] README/STATUS/INFORME sincronizan versión real de SKILL.
- [ ] Demo reproducible incluida en `scripts/` o removida del claim del tarball.
