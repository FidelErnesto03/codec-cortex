# Primer uso de CODEC-CORTEX

**Perfil: HCORTEX-TUTORIAL**

| Paso | Acción | Resultado esperado |
|---:|---|---|
| 1 | `cd cli` | Entrar al paquete CLI |
| 2 | `pip install -e .[dev]` | Instalar CLI y herramientas de prueba |
| 3 | `cortex --version` | Confirmar comando disponible |
| 4 | `cortex docstring canonicalize` | Generar referencia compacta desde CORTEX |
| 5 | `cortex benchmark --list` | Ver suites benchmark disponibles |

## Criterio

| Regla | Motivo |
|---|---|
| Usar `docs/README.md` como entrada | No exige conocer el protocolo |
| Usar `docs/hcortex/` para humanos | Mantiene lectura densa y auditada |
| Usar `docs/cortex/api/` para agentes | Mantiene fuente autocontenida y verificable |
