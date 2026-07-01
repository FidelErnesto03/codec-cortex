# Protocolo documental E3

**Perfil: HCORTEX-EXPLANATION**

| Formato | Audiencia | Rol |
|---|---|---|
| Markdown estándar | Público general | Entrada sin fricción |
| HCORTEX | Humanos técnicos | Lectura densa, tabular y auditable |
| CORTEX | Agentes y CLI | Fuente de verdad estructurada |

## Cadena de verdad

```text
docs/cortex/api/*.cortex
        ├── cortex verify --strict
        ├── cortex docstring <command>
        └── docs/hcortex/reference/
```

## Principio

> La documentación no debe describir el protocolo desde afuera; debe operar bajo el mismo protocolo.

## Riesgo controlado

| Riesgo | Control |
|---|---|
| Duplicar referencia API | Fuente única en `docs/cortex/api/` |
| Perder adopción humana | `docs/README.md` en Markdown estándar |
| Generar ayuda CLI desalineada | `cortex docstring` deriva desde CORTEX |
