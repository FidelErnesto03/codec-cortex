# Protocolo de Gate F2

**Objetivo:** demostrar que el roundtrip CORTEX↔HCORTEX es determinista y reversible. Los parsers son herramientas de transformación — no intérpretes del contenido. El LLM ya entiende CORTEX; la herramienta solo convierte entre formatos.

## 1. Independencia

Cada implementación:

- usa un lenguaje o codebase independiente;
- lee solo esta entrega y documentos superiores de Fase 1;
- no traduce `tools/hcortex_oracle.py`;
- no inspecciona la implementación de la otra;
- registra dudas como issues de ambigüedad.

Lenguajes recomendados: TypeScript y Rust, o Python y TypeScript con autores distintos.

### 1.1 Criterio de handoff entre agentes

CORTEX debe ser auto-documentante para agentes autónomos. Un agente debe poder:

- recibir un documento CORTEX 0.1 como orden de misión;
- parsear su glosario ($0) para entender el vocabulario del documento;
- extraer objetivo, restricciones, pasos y criterios del contenido;
- ejecutar la instrucción sin traducción externa ni texto plano adicional.

Este criterio se verifica experimentalmente: un agente externo recibe solo el documento CORTEX (más los artefactos normativos) y debe producir un parser funcional sin intervención humana. El Mini Gate F2 (BLP-003, 2026-07-17) demostró esta capacidad con agentes Go y Rust.

## 2. Alcance mínimo

Debe implementar:

- UTF-8 y secciones;
- `$0:format`;
- meta-declaraciones;
- sigilos locales y calificados;
- shapes cinco;
- contracts y focus;
- scalars y listas planas;
- enums y microtokens;
- namespaces y extensions;
- AST lógico;
- diagnostics requeridos.

No necesita implementar canonicalización ni HCORTEX.

## 3. Ejecución

1. Ejecutar todos los casos de `examples/manifest.json`.
2. Comparar valid/invalid.
3. Comparar AST ignorando únicamente metadata de source no exigida por el esquema.
4. Comparar códigos obligatorios.
5. Registrar divergencias.

## 4. Criterios de aprobación

```text
valid acceptance:             100%
invalid required-code:        100%
AST logical equivalence:      100%
profile-specific rules:       0
BLOCKER ambiguities open:     0
HIGH ambiguities open:        0
```

## 5. Preguntas de revisión externa

- ¿Está claro que la unidad es Idea y no value genérico?
- ¿Puede distinguir una declaración de `$0` de una Idea?
- ¿Puede resolver un shape sin profile externo?
- ¿Está determinada la interpretación de positional text?
- ¿Está claro cuándo un atom debe quoted?
- ¿Está claro que section title requiere espacio?
- ¿Puede emitir el mismo diagnostic primario?
- ¿Puede preservar una extensión opcional desconocida?
- ¿Comprende que local address no es durable identity?
- ¿Puede implementar sin conocer la skill histórica?

## 6. Estado

La validación interna de la entrega no aprueba el Gate. El Gate requiere actores independientes.
