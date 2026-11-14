# Agent benchmark package

Instrucciones autocontenidas para que un **agente autónomo** instale
`codec-cortex` desde PyPI y ejecute un benchmark **intensivo y extensivo** de
propiedades, beneficios y posibilidades del codec, de forma científica,
objetiva y documentada.

## Archivos

| Archivo | Qué es |
|---|---|
| [`codec-cortex-agent-benchmark.cortex`](codec-cortex-agent-benchmark.cortex) | **El paquete**. Autocontenido: glosario `$0` propio, 10 secciones, hipótesis con falsificador, matriz, métricas, protocolo, artefactos, compuertas, amenazas y anti-patrones |
| [`codec-cortex-agent-benchmark.hcortex.md`](codec-cortex-agent-benchmark.hcortex.md) | La misma verdad en HCORTEX, para lectura humana |
| [`SHA256SUMS`](SHA256SUMS) | Sello de los dos artefactos |

## Por qué está escrito en CORTEX

El paquete que enseña a medir CORTEX es a la vez una prueba de CORTEX: se parsea,
se canonicaliza, se renderiza y se recompila con la herramienta que va a medirse.
Si el toolchain falla, el agente lo detecta antes de gastar una sola llamada de
modelo.

## Cómo usarlo

1. Entregá el `.cortex` al agente como única fuente de instrucciones.
2. El agente ejecuta el self-check del paquete (`§2 PREPARATION`): instala
   `codec-cortex==1.0.1`, valida este archivo y exige `loss-report` con
   `reversible: true` y `losses: []`.
3. Congela `prereg.yaml` **antes** de la primera llamada a un modelo (compuerta
   G1) y recién entonces corre las fases P1–P4.

## Verificación de este paquete

Ejecutada con la propia herramienta (Python de referencia, 2026-11-14):

```bash
python -m codec_cortex validate    bench/agent-package/codec-cortex-agent-benchmark.cortex
python -m codec_cortex loss-report bench/agent-package/codec-cortex-agent-benchmark.cortex
python -m codec_cortex to-hcortex  bench/agent-package/codec-cortex-agent-benchmark.cortex
python -m codec_cortex from-hcortex bench/agent-package/codec-cortex-agent-benchmark.hcortex.md
```

| Comprobación | Resultado |
|---|---|
| `validate` | valid |
| `loss-report` | `reversible: true`, `losses: []` |
| roundtrip `canonicalize(compile(render(x))) == canonicalize(x)` | exacto |
| sello | verificar con `sha256sum -c SHA256SUMS` |

## Alcance

El paquete **no** promete que CORTEX gane: define cómo medirlo para que cualquier
resultado —a favor o en contra— sea evidencia. Un benchmark que no puede fallar
no es un benchmark.
