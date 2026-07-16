# CODEC-CORTEX v0.6.x — Aviso de congelación y transición

**Estado:** `historical-experimental`  
**Fecha efectiva:** `2026-07-16`  
**Repositorio:** `FidelErnesto03/codec-cortex`  
**Autoridad:** Plan `CCX-CORE-PROJECT-PLAN-001`

> Esta línea queda congelada para desarrollo funcional. No constituye el estándar CORTEX ni la implementación de referencia futura.

## Motivo

La línea v0.6.x combina responsabilidades que el nuevo diseño separa de manera constitucional:

- representación y parseo;
- HCORTEX;
- CRUD y transacciones;
- runtime y sesiones;
- aprendizaje y elevación de conocimiento;
- plantillas de agente;
- vocabularios cognitivos;
- seguridad y firma;
- benchmarks, documentación histórica y artefactos generados.

Continuar añadiendo capacidades sobre esta base aumentaría el acoplamiento y dificultaría demostrar interoperabilidad independiente.

## Política de congelación

Desde la fecha efectiva solo se aceptan:

1. correcciones de seguridad;
2. documentación de transición;
3. cambios indispensables para exportación o migración;
4. preservación de evidencia histórica.

Quedan prohibidos:

- nuevas features;
- nuevas capacidades de learning, runtime o gobierno;
- cambios de sintaxis presentados como estándar;
- nuevas afirmaciones de conformidad;
- releases que se anuncien como CORTEX Standard o Reference Codec.

## Identidad de esta línea

Esta línea debe ser tratada como:

```text
codec-cortex-lab
historical-experimental
not-standard
not-reference-codec
```

El renombrado y archivado administrativo del repositorio deberá realizarse al crear los repositorios limpios.

## Destino de los componentes

Los componentes heredados se evaluarán mediante fichas `reuse / rewrite / reject`. Ningún módulo será copiado por conveniencia ni conservará autoridad normativa por existir en Python.

## Próximas autoridades

```text
cortex-standard  -> especificación normativa
codec-cortex     -> implementación de referencia limpia
cortex-profiles  -> perfiles y vocabularios opcionales
```

Hasta que existan esas autoridades, ningún archivo de este repositorio debe interpretarse como Standard 1.0.
