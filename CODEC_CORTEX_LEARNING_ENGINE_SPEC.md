# Especificación de Construcción — Motor de Aprendizaje CODEC-CORTEX

**Documento para agente de desarrollo autónomo**  
**Propósito:** implementar, probar, auditar técnicamente y certificar un motor local de aprendizaje para CODEC-CORTEX.  
**Estado del documento:** especificación ejecutable / contrato de entrega.  
**Idioma semántico:** español.  
**Lenguaje estructural sugerido para código y sigilos:** inglés.  

---

## 0. Mandato ejecutivo

Construir un **motor determinístico de aprendizaje contextual** para CODEC-CORTEX que opere sobre un workspace canónico `.cortex/`, sin sobrecargar el `brain.cortex`, sin convertir al LLM/SLM en mutador directo de memoria, y optimizando el rendimiento contextual mediante índices de score reconstruibles.

El motor debe soportar dos vías de aprendizaje:

1. **Aprendizaje por candidatos**: detección contextual de entradas candidatas, scoring basado en progresión áurea/Fibonacci y propuesta de elevación.
2. **Aprendizaje por políticas**: políticas solicitadas por el usuario, formalizadas en `learn-policies.cortex`, que autorizan al motor a ejecutar elevaciones cuando sus condiciones se cumplen.

El resultado esperado de la implementación es un **paquete comprimido instalable localmente** en el proyecto CODEC-CORTEX, con pruebas de regresión, pruebas unitarias, validadores, documentación operativa y reporte de certificación.

---

## 1. Principios no negociables

### 1.1 Separación de responsabilidades

El sistema debe distinguir estrictamente:

| Artefacto | Responsabilidad | Fuente de verdad | Cargado por LLM por defecto |
|---|---|---:|---:|
| `.cortex/brain.cortex` | Memoria operativa del agente | Sí | Sí, según perfil |
| `.cortex/learn-policies.cortex` | Gobierno del aprendizaje | Sí | No |
| `.cortex/index/learn-index.json` | Índice de rendimiento y score | No, reconstruible | No |
| `.cortex/MANIFEST.cortex` | Mapa canónico de artefactos | Sí | No |
| `.cortex/cache/*` | Cache auxiliar | No | No |

### 1.2 El score favorece rendimiento, no auditoría

El score existe para acelerar:

- selección contextual;
- priorización de carga;
- detección de candidatos;
- elevación controlada;
- enfriamiento operativo de entradas poco relevantes;
- reducción del volumen leído por el modelo.

El score **no** debe diseñarse como ledger, historia, bitácora o evidencia legal. Puede contener hashes mínimos para invalidación técnica, pero no debe transformarse en auditoría de aprendizaje.

### 1.3 Índices reconstruibles

Todo índice de score debe poder reconstruirse a partir de:

```text
.cortex/brain.cortex + .cortex/learn-policies.cortex + versión del motor
```

Si se borra `.cortex/index/learn-index.json`, el sistema debe regenerarlo sin pérdida de conocimiento canónico.

### 1.4 El LLM no edita memoria ni políticas directamente

El LLM/SLM puede:

- interpretar solicitudes del usuario;
- pedir al motor que proponga una política;
- pedir explicación de candidatos;
- presentar diffs al usuario;
- solicitar al motor aplicar una operación confirmada.

El LLM/SLM no debe:

- editar `brain.cortex` directamente;
- editar `learn-policies.cortex` directamente;
- aplicar elevaciones sin pasar por el motor;
- inventar scores;
- omitir validaciones del motor.

### 1.5 Determinismo

El motor debe ser determinístico:

- no debe llamar a LLMs;
- no debe depender de servicios remotos;
- no debe usar tiempo actual para alterar resultados salvo campos explícitos de cache;
- debe producir la misma salida para el mismo `brain`, la misma política y la misma versión del algoritmo.

### 1.6 Sin `learn-ledger.cortex` en esta fase

No implementar `learn-ledger.cortex` como requisito. La auditoría del proceso de aprendizaje no es objetivo de esta fase. La certificación debe auditar el **software y sus pruebas**, no generar una bitácora permanente de cada aprendizaje.

---

## 2. Objetivo funcional

Implementar un subsistema llamado provisionalmente:

```text
Cortex Learning Engine / CLE
```

El CLE debe:

1. Inicializar un workspace `.cortex/`.
2. Localizar `brain.cortex` y `learn-policies.cortex` mediante `MANIFEST.cortex`.
3. Validar políticas de aprendizaje.
4. Escanear `brain.cortex` sin modificarlo.
5. Calcular scores e índices de rendimiento.
6. Detectar candidatos a elevación.
7. Aplicar políticas de aprendizaje autorizadas.
8. Proponer o ejecutar elevaciones según política.
9. Producir parches/diffs antes de modificar archivos canónicos.
10. Ejecutar regresión y certificación local.

---

## 3. Alcance de esta fase

### 3.1 Incluido

- Directorio `.cortex/` como workspace canónico.
- `MANIFEST.cortex` mínimo.
- `brain.cortex` como memoria operativa.
- `learn-policies.cortex` como política externa.
- `index/learn-index.json` como índice de rendimiento reconstruible.
- CLI `cortex learn ...` o integración equivalente al CLI existente.
- Scoring áureo/Fibonacci.
- Detección de candidatos.
- Evaluación de políticas.
- Elevación controlada.
- Dry-run obligatorio para mutaciones.
- Pruebas unitarias, integración y regresión.
- Paquete comprimido instalable localmente.

### 3.2 Excluido

- MCP enterprise.
- LLM runtime remoto.
- Vector database.
- RAG externo.
- Fine-tuning.
- Auditoría histórica de aprendizaje.
- `learn-ledger.cortex`.
- Promoción libre e irrestricta a conocimiento crítico.
- Borrado automático de conocimiento canónico.

---

## 4. Estructura canónica esperada

El agente debe implementar o generar esta estructura:

```text
.cortex/
  MANIFEST.cortex
  brain.cortex
  learn-policies.cortex
  index/
    learn-index.json
  cache/
    fingerprints.json
    candidates.json
```

### 4.1 `.cortex/MANIFEST.cortex`

Debe declarar los artefactos del workspace.

Ejemplo mínimo:

```cortex
# -- $0: GLOSSARY --
GSIG:IDN{sigil:"IDN", name:"identity", type:"attrs", risk:"B", description:"workspace identity"}
GSIG:REF{sigil:"REF", name:"reference", type:"attrs", risk:"B", description:"workspace file reference"}
GSIG:CNST{sigil:"CNST", name:"constraint", type:"attrs", risk:"H", description:"workspace hard rule"}

# -- $1: IDENTITY --
IDN:workspace{name:"codec_cortex_workspace", version:"0.1.0"}

# -- $2: FILES --
REF:brain{path:".cortex/brain.cortex", role:"operational_memory", required:true, canonical:true}
REF:learn_policy{path:".cortex/learn-policies.cortex", role:"learning_policy", required:false, canonical:true}
REF:learn_index{path:".cortex/index/learn-index.json", role:"learning_performance_index", required:false, canonical:false, rebuildable:true}

# -- $3: CONSTRAINTS --
CNST:no_direct_llm_mutation{rule:"LLM/SLM must request mutations through the learning engine", severity:"blocking"}
CNST:index_rebuildable{rule:"learning index is derived and rebuildable; it is not canonical memory", severity:"blocking"}
```

### 4.2 `.cortex/brain.cortex`

Debe seguir siendo la memoria operativa del agente. No debe contener políticas extensas de aprendizaje ni scores de runtime.

Puede contener una referencia mínima:

```cortex
REF:learn_policy{path:".cortex/learn-policies.cortex", role:"external_learning_policy", required:false}
```

### 4.3 `.cortex/learn-policies.cortex`

Debe contener reglas explícitas para aprendizaje.

Debe ser autocontenido y tener glosario mínimo propio.

Ejemplo base:

```cortex
# -- $0: GLOSSARY --
GSIG:IDN{sigil:"IDN", name:"identity", type:"attrs", risk:"B", description:"policy identity"}
GSIG:POL{sigil:"POL", name:"policy", type:"attrs", risk:"M", description:"learning policy"}
GSIG:THR{sigil:"THR", name:"threshold", type:"attrs", risk:"M", description:"learning thresholds"}
GSIG:GTE{sigil:"GTE", name:"gate", type:"attrs", risk:"H", description:"policy gate"}
GSIG:PRT{sigil:"PRT", name:"protected", type:"attrs", risk:"H", description:"protected targets"}

# -- $1: IDENTITY --
IDN:learn_policies{name:"default_learning_policies", version:"0.1.0", target:".cortex/brain.cortex"}

# -- $2: SCORING --
THR:golden_fibonacci{observed:1, repeated:2, pattern:3, candidate:5, ask_user:8, strong_candidate:13, critical:21}

# -- $3: PROTECTED TARGETS --
PRT:critical_sigils{items:"IDN|AXM|CNST:blocking|CLAIM|LIM", mutation:"explicit_user_confirmation"}

# -- $4: CANDIDATE-DRIVEN LEARNING --
POL:candidate_detection{source:"brain", scan_sigils:"WRK|SES|LNG|RSK|NXT|CLAIM|LIM", action:"score", algorithm:"golden_fibonacci_v1"}
POL:candidate_elevation{source:"SES|LNG", target:"LNG|KNW", when:"promotion_score>=8", action:"propose", requires:"user_confirmation"}

# -- $5: POLICY-DRIVEN LEARNING --
POL:auto_ses_to_lng{source:"SES", target:"LNG", when:"promotion_score>=8|user_validated=true", action:"apply", requires:"policy_authorized"}
POL:auto_lng_to_knw{source:"LNG", target:"KNW", when:"promotion_score>=13|user_validated=true|risk_weight>=8", action:"apply", requires:"admin_policy"}

# -- $6: GATES --
GTE:default_mutation{action:"mutate_brain", default:"dry_run_first"}
GTE:critical_mutation{targets:"IDN|AXM|CNST:blocking|CLAIM|LIM|KNW", default:"block_unless_admin_policy"}
```

### 4.4 `.cortex/index/learn-index.json`

Debe ser un índice de rendimiento, no memoria.

Esquema conceptual:

```json
{
  "schema_version": "0.1.0",
  "engine_version": "0.1.0",
  "brain_hash": "sha256:...",
  "policy_hash": "sha256:...",
  "algorithm": "golden_fibonacci_v1",
  "entries": {
    "LNG:example": {
      "entry_id": "LNG:example",
      "selector": "LNG:example",
      "fingerprint": "sha256:...",
      "hotness_score": 13,
      "promotion_score": 8,
      "risk_weight": 5,
      "read_priority": "P1",
      "candidate": true,
      "suggested_action": "propose_elevation",
      "signals": ["repeated", "user_validated"],
      "hits": 4
    }
  }
}
```

Debe ser invalidado si cambia:

- `brain_hash`;
- `policy_hash`;
- `engine_version`;
- `algorithm`.

---

## 5. Modelo de aprendizaje

## 5.1 Aprendizaje por candidatos

El motor detecta señales empíricas en `brain.cortex`, calcula score y propone elevación.

Flujo:

```text
brain.cortex
  → scan determinístico
  → fingerprints
  → señales
  → scoring Fibonacci
  → learn-index.json
  → candidatos ordenados
  → propuesta de elevación
```

### Señales mínimas

| Señal | Peso sugerido | Descripción |
|---|---:|---|
| `observed` | 1 | Entrada vista o registrada una vez |
| `repeated` | 2 | Repetición dentro de una misma sesión o contexto |
| `pattern` | 3 | Patrón recurrente entre entradas similares |
| `decision_relevant` | 5 | Afecta una decisión de diseño, arquitectura o operación |
| `user_validated` | 8 | El usuario validó o corrigió explícitamente el conocimiento |
| `risk_preventing` | 13 | Previene error significativo, regresión o pérdida contextual |
| `critical` | 21 | Afecta restricciones, identidad, claims, seguridad o límites |

### Umbrales mínimos

| Score | Interpretación | Acción por defecto |
|---:|---|---|
| 1 | Observado | Indexar |
| 2 | Repetido | Mantener caliente |
| 3 | Patrón leve | Aumentar prioridad de lectura |
| 5 | Candidato | Mostrar en candidatos |
| 8 | Atención humana | Proponer elevación |
| 13 | Fuerte candidato | Prioridad alta / posible política |
| 21 | Crítico | Bloquear automatismo común |

### Regla importante

```text
El score no eleva por sí solo. El score ordena, prioriza y recomienda.
```

La elevación automática solo ocurre si existe una política explícita que lo autoriza.

---

## 5.2 Aprendizaje por políticas

El usuario puede solicitar políticas como:

- “Cuando una lección aparezca varias veces y yo la valide, elévala a conocimiento”.
- “Si un riesgo se repite en tres sesiones, súbelo a prioridad P1”.
- “Si un patrón evita regresiones, conviértelo en regla operativa”.

El LLM debe transformar esa intención en una solicitud al motor, no en edición directa.

Flujo:

```text
Usuario
  → LLM interpreta intención
  → motor propone política formal
  → usuario confirma
  → motor guarda en learn-policies.cortex
  → motor aplica en futuros scans
```

### Tipos de política

| Tipo | Ejemplo | Riesgo |
|---|---|---:|
| `score_policy` | modificar pesos/umbrales | Medio |
| `candidate_policy` | cambiar detección de candidatos | Medio |
| `elevation_policy` | autorizar SES→LNG o LNG→KNW | Alto |
| `priority_policy` | alterar prioridad de carga | Medio |
| `protection_policy` | proteger/desproteger sigilos | Alto |

### Modos de acción

| Acción | Significado |
|---|---|
| `score` | solo calcular score |
| `propose` | generar candidato o diff, sin aplicar |
| `apply` | aplicar si la política lo permite |
| `block` | impedir mutación |

### Gating mínimo

| Elevación | Política común | Política admin | Confirmación humana inmediata |
|---|---:|---:|---:|
| `WRK → SES` | Permitida | Permitida | No siempre |
| `SES → LNG` | Permitida con política | Permitida | No siempre |
| `LNG → KNW` | No por defecto | Permitida | Según política |
| `CLAIM → KNW` | No | Permitida solo explícita | Recomendada |
| `CNST/AXM/IDN` | No | Muy restringida | Sí |
| `delete/decay KNW` | No | Muy restringida | Sí |

---

## 6. Algoritmo de scoring orientado a rendimiento

### 6.1 Scores mínimos

No usar un único score global. Implementar al menos:

```text
hotness_score      → recurrencia, actualidad y uso contextual
promotion_score    → aptitud para elevación semántica
risk_weight        → costo de omitir o degradar la entrada
read_priority      → prioridad de carga P0-P5
```

### 6.2 Pseudocódigo

```python
def rebuild_index(brain, policies, engine_version):
    ast = parse_cortex(brain)
    policy = parse_policies(policies)
    brain_hash = sha256(brain)
    policy_hash = sha256(policies)

    entries = []
    for entry in ast.entries:
        if not policy.scan_allows(entry):
            continue
        fingerprint = stable_fingerprint(entry)
        signals = detect_signals(entry, ast, policy)
        hotness = score_hotness(signals, policy)
        promotion = score_promotion(signals, policy)
        risk = score_risk(entry, signals, policy)
        priority = derive_read_priority(entry, hotness, promotion, risk, policy)
        candidate = promotion >= policy.threshold("candidate")
        entries.append(index_record(entry, fingerprint, hotness, promotion, risk, priority, candidate, signals))

    return LearnIndex(
        brain_hash=brain_hash,
        policy_hash=policy_hash,
        engine_version=engine_version,
        entries=entries,
    )
```

### 6.3 Derivación de prioridad de lectura

Regla sugerida:

```text
P0 = FCS, OBJ, CNST:blocking, STP o equivalente crítico
P1 = riesgo alto, score crítico, decisión activa, política explícita
P2 = conocimiento activo o candidato fuerte
P3 = patrón útil pero no urgente
P4 = referencia histórica o baja recurrencia
P5 = archivo, historia fría, contexto extenso no inmediato
```

### 6.4 Enfriamiento operativo

El motor puede reducir `read_priority` en el índice, pero no debe borrar ni degradar semánticamente una entrada del `brain.cortex` por esa sola razón.

```text
Enfriar lectura ≠ degradar conocimiento.
```

---

## 7. Elevación de conocimiento

### 7.1 Definición

“Elevación” significa mover o transformar una entrada a una capa de mayor valor operativo.

Ejemplos:

```text
WRK → SES
SES → LNG
LNG → KNW
RSK recurrente → CNST candidate/proposal
NXT recurrente → workflow rule proposal
```

### 7.2 Modos de elevación

| Modo | Descripción |
|---|---|
| `propose` | El motor genera diff, no aplica |
| `apply_policy` | El motor aplica porque existe política válida |
| `apply_confirmed` | El motor aplica tras confirmación explícita |
| `block` | El motor rechaza la elevación |

### 7.3 Requisitos de patch

Toda elevación debe producir primero un patch/diff:

```text
- entrada origen
- entrada destino propuesta
- razón resumida
- política aplicada, si existe
- score que la habilita
- archivos afectados
```

### 7.4 Mutación segura

Secuencia obligatoria:

```text
parse brain
parse policies
rebuild/validate index
plan patch
dry-run diff
apply only if mode allows
serialize
verify
rebuild index
run targeted tests
```

---

## 8. CLI requerido

El agente debe integrar estos comandos al CLI existente o crear un subcomando compatible.

### 8.1 Inicialización

```bash
cortex learn init --workspace .
```

Debe crear:

```text
.cortex/MANIFEST.cortex
.cortex/brain.cortex              # si no existe, usar template mínimo
.cortex/learn-policies.cortex     # si no existe, usar política default
.cortex/index/
.cortex/cache/
```

No debe sobrescribir archivos existentes sin `--force`.

### 8.2 Validación de workspace

```bash
cortex learn doctor
```

Debe validar:

- existe `.cortex/`;
- existe `MANIFEST.cortex`;
- paths declarados existen o son opcionales;
- `brain.cortex` parsea;
- `learn-policies.cortex` parsea si existe;
- índice está vigente o informa stale.

### 8.3 Política

```bash
cortex learn policy show
cortex learn policy validate
cortex learn policy propose --request "<texto del usuario>"
cortex learn policy apply --file proposed-policy.cortex --dry-run
cortex learn policy apply --file proposed-policy.cortex --confirm
```

`policy propose` no debe llamar a LLM. Si se necesita interpretación semántica, el LLM debe generar una propuesta intermedia y el motor solo validarla.

Alternativa aceptable:

```bash
cortex learn policy add --name auto_ses_to_lng --source SES --target LNG --when "promotion_score>=8|user_validated=true" --action apply --requires policy_authorized
```

### 8.4 Índice

```bash
cortex learn index rebuild
cortex learn index status
cortex learn index clean
```

### 8.5 Scanning y candidatos

```bash
cortex learn scan --json
cortex learn candidates --limit 10 --json
cortex learn explain --candidate <candidate_id>
```

### 8.6 Elevación

```bash
cortex learn elevate --candidate <candidate_id> --dry-run
cortex learn elevate --candidate <candidate_id> --apply --confirm
cortex learn elevate --policy <policy_id> --dry-run
cortex learn elevate --policy <policy_id> --apply
```

### 8.7 Perfil de carga orientado a rendimiento

```bash
cortex learn profile --budget 1000 --json
```

Debe devolver entradas recomendadas por `read_priority` y presupuesto estimado.

---

## 9. API interna sugerida

Implementar módulos similares a:

```text
cortex.learning.workspace
cortex.learning.policy
cortex.learning.index
cortex.learning.scoring
cortex.learning.candidates
cortex.learning.elevation
cortex.learning.cli
```

### 9.1 Clases/estructuras sugeridas

```python
@dataclass
class Workspace:
    root: Path
    manifest_path: Path
    brain_path: Path
    policy_path: Path | None
    index_path: Path

@dataclass
class LearningPolicy:
    id: str
    source: str
    target: str | None
    when: str
    action: Literal["score", "propose", "apply", "block"]
    requires: str

@dataclass
class ScoreRecord:
    entry_id: str
    selector: str
    fingerprint: str
    hotness_score: int
    promotion_score: int
    risk_weight: int
    read_priority: str
    candidate: bool
    suggested_action: str
    signals: list[str]

@dataclass
class Candidate:
    candidate_id: str
    source_entry: str
    target_layer: str
    promotion_score: int
    policy_id: str | None
    action: str
    reason: str
```

### 9.2 Parser de condiciones

Implementar un parser simple y determinístico para condiciones como:

```text
promotion_score>=8|user_validated=true|risk_weight>=5
```

Requisitos:

- soportar `|` como AND semántico inicial;
- soportar operadores `=`, `!=`, `>=`, `<=`, `>`, `<`;
- no usar `eval`;
- no ejecutar expresiones arbitrarias;
- fallar cerrado si la condición es inválida.

---

## 10. Pruebas requeridas

### 10.1 Unit tests

Cubrir como mínimo:

1. Descubrimiento de workspace `.cortex/`.
2. Parseo de `MANIFEST.cortex`.
3. Parseo de `learn-policies.cortex`.
4. Validación de políticas válidas.
5. Rechazo de políticas inválidas.
6. Cálculo de hash de brain y policy.
7. Invalidation de índice cuando cambia brain.
8. Invalidation de índice cuando cambia policy.
9. Fingerprint estable por entrada.
10. Scoring Fibonacci básico.
11. Derivación de `read_priority`.
12. Detección de candidatos.
13. Política `propose` no muta brain.
14. Política `apply` muta solo si está autorizada.
15. Protección de sigilos críticos.
16. Condiciones sin `eval`.
17. Dry-run genera diff.
18. Apply escribe archivo y luego verifica.

### 10.2 Integration tests

Casos mínimos:

#### Caso A — inicialización

```bash
cortex learn init --workspace tmp_project
cortex learn doctor
```

Resultado esperado: workspace válido.

#### Caso B — index rebuild

```bash
cortex learn index rebuild
cortex learn index status
```

Resultado esperado: índice vigente, reconstruible, JSON válido.

#### Caso C — candidatos

Usar un `brain.cortex` con varias entradas `SES` similares.

```bash
cortex learn scan --json
cortex learn candidates --limit 5 --json
```

Resultado esperado: al menos un candidato con score >= 5.

#### Caso D — elevación dry-run

```bash
cortex learn elevate --candidate <id> --dry-run
```

Resultado esperado: diff generado; brain sin cambios.

#### Caso E — elevación por política

Agregar política `SES → LNG` con `action:apply`.

```bash
cortex learn elevate --policy auto_ses_to_lng --apply
```

Resultado esperado: brain modificado solo si la condición se cumple.

#### Caso F — protección crítica

Intentar elevar/modificar `CNST:blocking` con política común.

Resultado esperado: operación bloqueada.

### 10.3 Regression tests

El agente debe ejecutar todas las pruebas existentes del proyecto antes y después.

Comandos orientativos:

```bash
pytest
cortex verify .cortex/brain.cortex --strict
cortex learn doctor
cortex learn index rebuild
cortex learn scan --json
```

Si el proyecto usa otro runner, adaptarse sin eliminar cobertura.

---

## 11. Auditoría técnica de implementación

Aunque no se requiere `learn-ledger.cortex`, sí se exige auditoría técnica del paquete.

El agente debe producir un reporte `CERTIFICATION_REPORT.md` con:

1. Hash del paquete generado.
2. Versión del motor.
3. Lista de archivos instalados/modificados.
4. Resultado de pruebas unitarias.
5. Resultado de pruebas de integración.
6. Resultado de regresión existente.
7. Confirmación de que no se usan llamadas LLM.
8. Confirmación de que no se usan llamadas de red.
9. Confirmación de que no se usa `eval` para políticas.
10. Confirmación de que el índice es reconstruible.
11. Confirmación de que `brain.cortex` no contiene scores ni políticas extensas.
12. Confirmación de que `learn-ledger.cortex` no fue implementado como dependencia.

### 11.1 Checks automáticos mínimos

```bash
python -m pytest
python -m compileall cli/src
python -m pip check
```

Además, buscar patrones prohibidos:

```bash
grep -R "openai\|anthropic\|requests\|httpx\|urllib" cli/src/cortex/learning || true
grep -R "eval(" cli/src/cortex/learning && exit 1 || true
grep -R "exec(" cli/src/cortex/learning && exit 1 || true
```

Nota: si el proyecto ya usa alguna dependencia HTTP en otro módulo, no bloquear globalmente. El bloqueo aplica al motor de aprendizaje.

---

## 12. Criterios de certificación

El paquete solo se considera certificado si cumple:

| Criterio | Obligatorio |
|---|---:|
| Existing tests pasan | Sí |
| New learning tests pasan | Sí |
| `learn init` idempotente | Sí |
| `learn doctor` detecta inconsistencias | Sí |
| `learn index rebuild` determinístico | Sí |
| Índice invalidado por hash | Sí |
| `learn scan` no muta brain | Sí |
| `learn candidates` ordena por prioridad | Sí |
| `learn elevate --dry-run` no muta | Sí |
| `learn elevate --apply` respeta política | Sí |
| Sigilos críticos protegidos | Sí |
| No uso de LLM | Sí |
| No uso de red | Sí |
| No uso de `eval`/`exec` | Sí |
| Paquete comprimido generado | Sí |

---

## 13. Entregable esperado del agente

El agente debe entregar un archivo comprimido:

```text
codec-cortex-learning-engine-<version>.tar.gz
```

Contenido mínimo:

```text
codec-cortex-learning-engine-<version>/
  README_INSTALL.md
  CERTIFICATION_REPORT.md
  PATCH_SUMMARY.md
  cli/
    ... cambios del motor ...
  tests/
    ... pruebas nuevas ...
  templates/
    .cortex/
      MANIFEST.cortex
      learn-policies.cortex
      brain.cortex
  schemas/
    learn-index.schema.json
  scripts/
    install_local.sh
    run_regression.sh
```

### 13.1 `README_INSTALL.md`

Debe explicar:

```bash
tar -xzf codec-cortex-learning-engine-<version>.tar.gz
cd codec-cortex-learning-engine-<version>
./scripts/install_local.sh /ruta/al/proyecto/codec-cortex
./scripts/run_regression.sh /ruta/al/proyecto/codec-cortex
```

### 13.2 `PATCH_SUMMARY.md`

Debe listar:

- archivos creados;
- archivos modificados;
- comandos agregados;
- decisiones técnicas;
- desviaciones respecto de esta especificación.

### 13.3 `CERTIFICATION_REPORT.md`

Debe incluir evidencia textual de ejecución de pruebas.

---

## 14. Plan de implementación recomendado

### Fase 1 — Descubrimiento

1. Inspeccionar estructura real del repo.
2. Detectar CLI actual.
3. Detectar parser existente de `.cortex`.
4. Detectar sistema de tests.
5. No modificar archivos hasta completar diagnóstico.

Salida: `PATCH_SUMMARY.md` inicial.

### Fase 2 — Workspace

1. Implementar `Workspace`.
2. Implementar `learn init`.
3. Implementar `learn doctor`.
4. Agregar templates.
5. Tests de idempotencia.

### Fase 3 — Políticas

1. Parser/loader de `learn-policies.cortex`.
2. Validación de políticas.
3. Parser seguro de condiciones.
4. Tests de rechazo seguro.

### Fase 4 — Índice y scoring

1. Fingerprints estables.
2. Scoring Fibonacci.
3. `learn index rebuild`.
4. `learn index status`.
5. JSON schema.

### Fase 5 — Candidatos

1. `learn scan`.
2. `learn candidates`.
3. `learn explain`.
4. Orden por rendimiento contextual.

### Fase 6 — Elevación

1. Planificador de patch.
2. Dry-run diff.
3. Apply con política.
4. Verificación post-write.
5. Protección crítica.

### Fase 7 — Certificación

1. Ejecutar tests existentes.
2. Ejecutar tests nuevos.
3. Ejecutar checks de seguridad local.
4. Generar paquete comprimido.
5. Generar reporte final.

---

## 15. Reglas de rechazo

El agente debe detener o bloquear la entrega si ocurre cualquiera de estos eventos:

1. El motor requiere conexión a internet para operar.
2. El motor requiere LLM para calcular scores.
3. El motor usa `eval` o `exec` para políticas.
4. `learn scan` modifica `brain.cortex`.
5. `learn index rebuild` escribe en `brain.cortex`.
6. Una política común permite modificar `IDN`, `AXM`, `CNST:blocking`, `CLAIM` o `LIM`.
7. El índice se trata como fuente canónica.
8. El paquete no incluye pruebas.
9. No pasan las pruebas existentes del proyecto.
10. El agente implementa `learn-ledger.cortex` como dependencia obligatoria.

---

## 16. Casos de ejemplo para pruebas

### 16.1 Brain de prueba

```cortex
# -- $0: GLOSSARY --
GSIG:SES{sigil:"SES", name:"session", type:"attrs", risk:"B", description:"session memory"}
GSIG:LNG{sigil:"LNG", name:"lesson", type:"attrs", risk:"M", description:"learned lesson"}
GSIG:KNW{sigil:"KNW", name:"knowledge", type:"attrs", risk:"M", description:"operational knowledge"}
GSIG:CNST{sigil:"CNST", name:"constraint", type:"attrs", risk:"H", description:"hard rule"}

SES:policy_externalization_1{topic:"learning policies", outcome:"policy should be external to brain", user_validated:true}
SES:policy_externalization_2{topic:"learning policies", outcome:"policy should be external to brain", user_validated:true}
SES:policy_externalization_3{topic:"learning policies", outcome:"policy should be external to brain", user_validated:true}
LNG:score_performance{lesson:"learning score exists to improve runtime performance, not auditability", user_validated:true}
CNST:blocking_rule{rule:"LLM must not mutate brain directly", severity:"blocking"}
```

Resultado esperado:

- Las tres `SES` similares generan candidato `SES → LNG`.
- `LNG:score_performance` puede tener alta prioridad de lectura.
- `CNST:blocking_rule` queda protegido.

### 16.2 Política de prueba

```cortex
POL:auto_validated_ses_to_lng{source:"SES", target:"LNG", when:"promotion_score>=8|user_validated=true", action:"apply", requires:"policy_authorized"}
```

Resultado esperado:

- El motor puede aplicar `SES → LNG` si la condición se cumple.
- Debe producir dry-run antes de apply.
- No debe tocar `CNST:blocking_rule`.

---

## 17. Salida esperada de `learn candidates --json`

Ejemplo:

```json
{
  "brain_hash": "sha256:...",
  "policy_hash": "sha256:...",
  "stale_index": false,
  "candidates": [
    {
      "candidate_id": "cand_001",
      "source_entries": [
        "SES:policy_externalization_1",
        "SES:policy_externalization_2",
        "SES:policy_externalization_3"
      ],
      "target": "LNG",
      "promotion_score": 13,
      "hotness_score": 13,
      "risk_weight": 5,
      "read_priority": "P1",
      "suggested_action": "elevate_to_lng",
      "policy_match": "POL:auto_validated_ses_to_lng"
    }
  ]
}
```

---

## 18. Resultado esperado de certificación

El agente debe terminar con una declaración similar:

```text
CERTIFICATION: PASS
Package: codec-cortex-learning-engine-0.1.0.tar.gz
Existing tests: PASS
Learning tests: PASS
Regression: PASS
No LLM calls: PASS
No network calls in learning engine: PASS
No eval/exec: PASS
Index rebuildable: PASS
Critical sigils protected: PASS
```

Si algo falla, debe entregar:

```text
CERTIFICATION: FAIL
Reason: <razón exacta>
Blocking issue: <sí/no>
Partial artifacts: <lista>
```

---

## 19. Resumen canónico para incorporar a SKILL posteriormente

Texto sugerido:

```text
CODEC-CORTEX learning is governed by two mechanisms:

1. Candidate-driven learning: the learning engine detects contextual recurrence, validation, risk and decision relevance, assigning golden-ratio/Fibonacci scores to optimize contextual performance and propose elevation.

2. Policy-driven learning: user-requested learning policies are stored outside brain.cortex in learn-policies.cortex. The LLM/SLM may request policy creation or modification through the learning engine, but must not mutate policies or brain memory directly.

Learning scores are runtime performance indexes. They optimize loading, candidate selection, elevation readiness and contextual pruning. They are derived, rebuildable and non-semantic. They are not canonical memory and not audit evidence.
```

---

## 20. Instrucción final al agente autónomo

Ejecuta esta especificación como contrato de trabajo.

Prioriza:

1. Compatibilidad con el CLI y tests existentes.
2. Determinismo.
3. No sobrecargar `brain.cortex`.
4. Índices reconstruibles orientados a rendimiento.
5. Políticas externas gestionadas por motor.
6. Mutaciones con dry-run y compuertas.
7. Certificación reproducible.
8. Paquete comprimido instalable localmente.

No declares éxito si no puedes generar el paquete comprimido y el reporte de certificación.
