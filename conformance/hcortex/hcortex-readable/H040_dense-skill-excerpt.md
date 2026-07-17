# Contexto CORTEX

## Sección 1

### objective: intent

- **goal:** Transformar contexto sin pérdida.
- **status:** current

### procedure: step1

- **action:** parsear CORTEX
- **status:** done
- **target:** AST

### procedure: step2

- **action:** renderizar HCORTEX
- **status:** done
- **target:** Markdown canónico

### knowledge: invariant

- **topic:** Reversibilidad
- **content:** compile(render(AST)) produce el mismo AST.

### relation: proof

- **source:** $1:HDL:step1
- **predicate:** precedes
- **target:** $1:HDL:step2
