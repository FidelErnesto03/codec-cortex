# Consideraciones de seguridad HCORTEX 0.1

**Document ID:** `HCORTEX-SECURITY-001`

## 1. Modelo de amenaza

HCORTEX puede ser editado por humanos, generado por herramientas o recibido de agentes externos. Debe tratarse como entrada no confiable.

## 2. Riesgos

| Riesgo | Impacto | Control requerido |
|---|---|---|
| HTML/script embebido | ejecución al previsualizar | sanitización y no ejecución durante compile |
| payload oculto en comentarios | bypass de edición visible | prohibición D4-002 + `H481` |
| tables excesivas | agotamiento de memoria/CPU | límites configurables |
| fences gigantes/no cerrados | DoS o parse ambiguo | streaming, límites, `H461/H490` |
| Unicode confusable | identidad engañosa | IDs ASCII; contenido NFC salvo bloque |
| extensión requerida maliciosa | ejecución externa | preservar, nunca ejecutar implícitamente |
| links/includes | exfiltración o dependencia de red | compile offline y sin fetch |
| contradicción metadata/heading | sustitución de identidad | error duro `H432` |
| READABLE confundido con canon | pérdida silenciosa | marcador de modo y `H402/H485` |
| diagnostics con secretos | fuga de datos | mensajes acotados y redacción segura |

## 3. Límites mínimos configurables

- bytes totales;
- líneas;
- secciones;
- Ideas;
- filas por tabla;
- columnas;
- longitud de celda;
- tamaño de cuerpo/bloque;
- profundidad y bytes de JSON de metadata;
- cantidad de extensiones y entradas de glosario.

Exceder un límite produce error. No se trunca.

## 4. Render seguro

El renderer canónico:

- no ejecuta Markdown;
- no resuelve enlaces;
- no evalúa bloques;
- no descarga recursos;
- no interpreta VIEW;
- emite únicamente comentarios HTML de metadata conocidos.

## 5. Compile seguro

El compiler:

- opera offline;
- valida UTF-8 antes de parsear;
- valida JSON con límites;
- usa parsers deterministas;
- evita regex con backtracking no acotado;
- conserva extensiones opacas;
- no hace inferencia LLM.
