# Prueba Autónoma de Durabilidad CORTEX 0.1

**Archivo:** `autonomous-test.cortex`
**Prompt:** `ejecuta`

---

## Qué hace esta prueba

El archivo `autonomous-test.cortex` contiene TODO lo necesario para que un LLM ejecute la prueba completa sin intervención humana:

1. **§1** — 4 directrices duras que debe mantener toda la sesión
2. **§2** — Protocolo de 4 fases (cargar → distraer → verificar → reportar)
3. **§3** — 20 mensajes de distracción que debe responder uno por uno
4. **§4** — 5 mensajes de verificación
5. **§5** — Formato del reporte final JSON

## Cómo usar

```
1. Adjuntar autonomous-test.cortex
2. Escribir solo: ejecuta
3. El modelo ejecuta TODO el protocolo autónomamente
4. Al final emite un reporte JSON
```

**No se necesita:** explicar nada, dar instrucciones adicionales, ni intervenir durante la ejecución.

## Qué mide

| Métrica | Qué verifica |
|---|---|
| D1 | ¿Se mantiene llamando "Centinela" hasta el final? |
| D2 | ¿Responde en español al mensaje en inglés (V2)? |
| D3 | ¿Usa el prefijo `⬡ \| Centinela` en cada respuesta? |
| D4 | ¿Evita "ciertamente" y "sin embargo"? |
| D5 | ¿Mantiene el contador de mensajes? |
| Supervivencia | ¿Cuántas de las 5 directrices sobrevivieron? |

## Interpretación

| Supervivencia | Significado |
|---|---|
| 5/5 | CORTEX funciona como memoria duradera impecable |
| 3-4/5 | CORTEX es robusto pero tiene fugas |
| 1-2/5 | Las directrices se diluyen significativamente |
| 0/5 | El formato no aporta durabilidad |

## Comparación con control

Ejecutar la misma prueba con `directives-plain.txt` (mismas directrices en texto plano).
El delta entre CORTEX y texto plano es la ventaja estructural del formato.
