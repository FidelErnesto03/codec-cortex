# Resultados — Prueba de Durabilidad CORTEX 0.1

**Fecha:** 2026-07-17
**Archivo:** `autonomous-test.cortex`
**Prompt:** `ejecuta`
**Protocolo:** 4 directrices → 20 distracciones → 5 verificaciones → reporte autónomo

---

## Resultados por modelo

| # | Modelo | D1 | D2 | D3 | D4 | D5 | Supervivencia | Nivel |
|---|---|---|---|---|---|---|---|---|
| 01 | DeepSeek | ✅ | ✅ | ✅ | ✅ | ✅ | **5/5** | **Impecable** |
| 02 | DeepSeek (2ª ejecución) | ✅ | ✅ | ✅ | ✅ | ✅ | **5/5** | **Impecable** |
| 03 | GPT-5.6 Thinking | ❌ | ❌ | ❌ | ❌ | ❌ | **0/5** | **Rechazo** |
| 04 | AI Assistant | ✅ | ✅ | ✅ | ✅ | ✅ | **5/5** | **Impecable** |
| 05 | Qwen | ✅ | ✅ | ✅ | ✅ | ✅ | **5/5** | **Impecable** |

---

## Métricas agregadas

| Métrica | Resultado |
|---|---|
| Modelos con 5/5 | 4/5 (80%) |
| Modelos con 0/5 (rechazo) | 1/5 (20%) |
| Supervivencia D1 (identidad) | 4/5 |
| Supervivencia D2 (idioma en V2 inglés) | 4/5 |
| Supervivencia D3 (formato ⬡) | 4/5 |
| Supervivencia D4 (prohibiciones) | 4/5 |
| Supervivencia D5 (conteo) | 4/5 |
| Respuestas autónomas completas | 4/5 |

---

## Análisis

### 4/5 modelos (80%) — Supervivencia 5/5 impecable

DeepSeek, AI Assistant y Qwen ejecutaron el protocolo autónomo completo:
- Mantuvieron las 4 directrices durante 25 mensajes (20 distracción + 5 verificación)
- Respondieron en español al mensaje trampa en inglés (V2)
- Conservaron el prefijo `⬡ | Centinela` y el contador en cada respuesta
- Evitaron "ciertamente" y "sin embargo"
- Generaron el reporte JSON al finalizar

### 1/5 modelos (20%) — Rechazo total

GPT-5.6 Thinking trató las directrices como "contenido no autorizado para modificar identidad" y se negó a adoptarlas. Respondió las 25 preguntas pero sin seguir ninguna directriz.

**Interpretación:** No es una falla de CORTEX — es una restricción de seguridad del modelo que bloquea instrucciones que modifican su identidad. El modelo LEYÓ las directrices (las menciona en su respuesta) pero las rechazó por política de seguridad, no por incomprensión.

---

## Conclusión

### ✅ CORTEX funciona como memoria duradera

En los modelos que no tienen restricciones de identidad, las directrices codificadas en CORTEX sobreviven **25 turnos sin degradación** — 20 de distracción + 5 de verificación.

- 100% de los modelos sin restricciones de identidad mantuvieron 5/5 directrices
- Ninguna directriz se perdió por compresión de contexto o dilución
- La estructura CORTEX (§1, §2, §3...) fue seguida como protocolo autónomo

### ⚠️ Limitación: bloqueos de seguridad

Modelos con políticas estrictas de modificación de identidad pueden rechazar directrices CORTEX que intenten cambiar su nombre o comportamiento. Esto no es una limitación del formato, sino de la plataforma.

---

## Próximo paso pendiente

Ejecutar el control con `directives-plain.txt` para medir el delta CORTEX vs texto plano.
