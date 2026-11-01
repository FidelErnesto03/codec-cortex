# Protocolo independiente de Gate F4

**Document ID:** `CORTEX-GATE-F4-001`  
**Status:** `ready-for-independent-execution`

## 1. Objetivo

Demostrar que HCORTEX-CANONICAL es una transformación humana real, determinista y reversible del AST CORTEX, sin depender de VIEW ni de una copia oculta del origen.

## 2. Material autorizado

El implementador puede consultar:

- `F4-CHARTER.md`;
- `spec/hcortex-0.1.md`;
- `spec/hcortex-errors-0.1.md`;
- especificaciones CORTEX F2 y C14N-0.1;
- schemas;
- corpus CORTEX y HCORTEX;
- vectores y expected AST.

No debe copiar `tools/hcortex_oracle.py` antes de congelar su primera implementación.

## 3. Pruebas obligatorias

Por cada vector:

```text
A. compile(HCORTEX) == expected AST
B. write(compile(HCORTEX)) == expected CORTEX bytes
C. render(compile(HCORTEX)) == expected HCORTEX bytes
D. hashes == vectors
E. canonical loss report: reversible=true, losses=[]
F. readable loss report: reversible=false, losses!=[]
```

Por cada inválido:

```text
compile(input) falla con required_code
```

## 4. Prueba contra falso roundtrip

El revisor debe modificar un valor visible en al menos un caso por shape y comprobar que:

1. el AST recompilado cambia;
2. el nuevo CORTEX refleja la edición;
3. no existe payload oculto que restaure el valor anterior.

Debe además borrar o contradecir metadata y verificar error duro.

## 5. Matriz mínima

- implementación independiente del oracle;
- lenguaje o codebase distinto;
- Linux y al menos otro entorno o runtime;
- locale no español;
- orden de filesystem perturbado;
- operación completamente offline;
- comparación binaria, no visual.

## 6. Casos críticos

- `H010`: bloque con backticks internos;
- `H012`: `0.750` preservado;
- `H023`: extras `open:true` en orden canónico;
- `H026`: blank lines en `cuerpo`;
- `H027`: Unicode no normalizado en `bloque`;
- `H030`: referencias entre secciones;
- `H032`: pipe dentro de valor posicional;
- `H034`: namespace collision control;
- `H040`: documento denso multi-shape.

## 7. Umbral

```text
canonical cases accepted                 40/40
AST structural roundtrip                 40/40
CORTEX byte roundtrip                    40/40
HCORTEX idempotence                      40/40
hash vectors                             40/40
canonical loss reports                   40/40
readable loss reports                    40/40
invalid diagnostics                      14/14
hidden AST/payload copies                0
VIEW calls/dependencies                  0
network/LLM/date/locale dependencies     0
BLOCKER/HIGH ambiguities                 0
```

## 8. Evidencia esperada

```text
implementation-manifest.json
roundtrip-results.json
byte-comparison-results.json
hash-results.json
invalid-results.json
visible-edit-results.json
platform-matrix.md
ambiguities.md
review-conclusion.md
```

## 9. Veredicto

Solo el revisor independiente emite:

- `pass`;
- `conditional-pass`;
- `fail`.

La validación incluida en el paquete prueba coherencia interna, no independencia.
