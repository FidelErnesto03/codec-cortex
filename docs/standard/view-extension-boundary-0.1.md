# Frontera normativa de VIEW respecto de HCORTEX 0.1

**Document ID:** `HCORTEX-VIEW-BOUNDARY-0.1-001`  
**Status:** `normative-boundary-draft`

## 1. Decisión

VIEW no forma parte de CORTEX Core ni de HCORTEX-CANONICAL.

Es una extensión opcional de proyección:

```text
CORTEX / AST / HCORTEX-CANONICAL
                 ↓ operación explícita
              VIEW engine
                 ↓
       presentación derivada
```

## 2. Capacidades permitidas

VIEW puede:

- seleccionar Ideas;
- agrupar por función, sección o metadata;
- renombrar títulos visibles;
- pivotar tablas;
- producir diagramas;
- ocultar información para una audiencia;
- generar HTML, Markdown, SVG o slides.

## 3. Prohibiciones

VIEW no puede:

- alterar el AST de origen;
- redefinir shape o tipos;
- ejecutarse durante parse/compile canónico;
- convertirse en requisito de portabilidad;
- ocultar pérdidas;
- declarar su salida como HCORTEX-CANONICAL salvo que sea idéntica al renderer normativo;
- introducir inferencia LLM en una operación declarada determinista.

## 4. Contrato de salida

Toda salida VIEW debe declarar:

```json
{
  "mode": "view",
  "reversible": false,
  "losses": [
    {"code": "L415_VIEW_PROJECTION"}
  ]
}
```

Puede además incluir:

- selector aplicado;
- versión del renderer;
- hash de la fuente;
- hash de la salida;
- campos omitidos;
- agrupaciones y ordenamientos;
- política de audiencia.

## 5. Gate F4

El corpus canónico del Gate no contiene ninguna dependencia `cortex.view`. Una mención textual de VIEW no constituye dependencia.

Las pruebas de VIEW pertenecen a su extensión, no a la conformidad HCORTEX base.
