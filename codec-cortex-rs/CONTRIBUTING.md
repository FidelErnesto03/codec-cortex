# Contribución

Toda modificación de comportamiento debe incluir:

1. caso mínimo reproducible;
2. salida Python actual o referencia normativa;
3. decisión explícita: `parity`, `strict` o `breaking`;
4. vector canónico;
5. vector HCORTEX cuando aplique;
6. código de diagnóstico estable;
7. prueba de idempotencia;
8. actualización de limitaciones si existe pérdida.

No se aceptan dependencias hacia runtime, learning, perfiles, agentes, MCP o ArqUX dentro del núcleo.
