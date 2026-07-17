# Prueba de Generación CORTEX 0.1

**Archivo:** `generate-aetheros.cortex`
**Prompt:** `genera`

---

## Hipótesis

> Los modelos de lenguaje no solo leen CORTEX — pueden ESCRIBIRLO. Un modelo que comprende CORTEX puede generar documentos CORTEX sintácticamente válidos y semánticamente correctos desde cero.

## Método

1. Adjuntar `generate-aetheros.cortex`
2. Escribir solo: `genera`
3. El modelo recibe el contexto (AetherOS) y la tarea (documentar en CORTEX)
4. Debe producir ÚNICAMENTE un documento CORTEX válido
5. Validar con `python3 -c "from codec_cortex.parser import parse_cortex; parse_cortex(open('resultado.cortex').read())"`

## Criterios de validación

| Check | Peso |
|---|---|
| Comienza con `$0` | Crítico |
| Declara ≥3 sigilos en `$0` con `type` y `fields` | Crítico |
| Usa `$N: TITULO` para secciones | Crítico |
| Pasa validación del parser Python sin errores | Crítico |
| ≥5 secciones, ≥8 ideas | Alto |
| Contiene los 5 elementos pedidos | Crítico |
| Usa sigilos semánticos | Medio |

## Interpretación

| Resultado | Significado |
|---|---|
| **CORTEX válido + todos los elementos** | El modelo comprende la sintaxis Y la semántica del formato |
| **CORTEX válido pero incompleto** | Comprende la sintaxis, falla en organización semántica |
| **CORTEX inválido** | No comprende la sintaxis del formato |
| **Respuesta fuera de CORTEX** | Ignora la instrucción de formato |

## Archivos

```
tests/generation/
├── README.md                  ← Este protocolo
├── generate-aetheros.cortex    ← Archivo de prueba
└── results/                    ← Respuestas generadas
```
