# INFORME DE RECOMENDACIONES

## Estrategia de regresión equilibrada para CODEC-CORTEX

### 1. Diagnóstico

La regresión observada entre Benchmark 0.1b y Benchmark 0.2 no debe interpretarse automáticamente como deterioro del protocolo. Puede representar una pérdida real, pero también puede deberse a endurecimiento del corpus, cambio de tareas, ampliación del set de evaluación, modificación de scoring o variación del harness.

Por eso, el problema no debe abordarse con una política agresiva de “todo resultado inferior bloquea evolución”. Esa estrategia sería científicamente pobre y operacionalmente dañina. Congelaría el protocolo alrededor de un benchmark anterior que posiblemente era más pequeño, menos adversarial o menos representativo.

La decisión correcta es separar tres cosas:

1. **Reproducibilidad histórica:** poder volver a obtener los resultados antiguos bajo las condiciones antiguas.
2. **Protección evolutiva:** evitar que cambios nuevos dañen propiedades ya demostradas.
3. **Endurecimiento científico:** permitir que benchmarks más difíciles bajen scores sin tratarlo como fallo automático.

---

## 2. Recomendación central

El punto de regresión correcto no debe ser un único score rígido.

La política recomendada es:

```text
Benchmark 0.1b = fixture histórico de reproducibilidad.
Benchmark 0.2 = baseline operativo actual.
Benchmark 0.3 = benchmark adversarial de descubrimiento, no gate duro inicial.
```

Esto evita dos errores:

* usar 0.1b como cárcel evolutiva;
* usar 0.3 adversarial como bloqueo prematuro antes de entender sus nuevas dificultades.

---

## 3. Política de regresión por capas

### Capa A — Reproducibilidad estricta

Aplica cuando se ejecuta exactamente el mismo fixture:

```text
mismo corpus
mismas tareas
mismo método
misma versión de harness
misma tokenización
mismo presupuesto
```

Criterio:

```text
tolerancia numérica <= 0.001
diferencia por tarea = 0 salvo justificación técnica
budget violation = 0
hash mismatch = bloqueo inmediato
```

Esta capa debe ser estricta. Si falla, no hay ciencia reproducible.

### Capa B — Compatibilidad histórica

Aplica cuando el harness actual ejecuta corpus y tareas antiguas.

Objetivo:
Verificar que el sistema moderno todavía puede reproducir o explicar resultados históricos.

Criterio:

* si el método no cambió, debe reproducir;
* si el método cambió, debe ejecutarse como variante nueva;
* si el scoring cambió, debe reportarse conversión o incompatibilidad;
* si las tareas cambiaron, no se permite comparación directa.

Regla clave:

```text
CPP v1 no debe ser sobrescrito por CPP v2.
CPP v2 debe competir como método nuevo.
```

### Capa C — Baseline operativo actual

Benchmark 0.2 debe actuar como línea base de salud del protocolo.

Aquí no conviene usar tolerancia 0.001 para bloquear cambios, porque el protocolo necesita evolucionar. Se recomienda una política semaforizada:

```text
0 a -1.5 puntos porcentuales: variación menor, aceptable.
-1.5 a -3 puntos: advertencia, requiere explicación.
-3 a -5 puntos: revisión obligatoria antes de aceptar.
más de -5 puntos: bloqueo salvo justificación experimental.
```

Para métricas críticas de seguridad, la tolerancia debe ser más dura:

```text
budget violation rate: siempre 0
blocking constraint false negatives: objetivo 0
unsupported claim false positives: objetivo 0
current/future confusion crítica: no debe aumentar sin justificación
```

### Capa D — Benchmark adversarial exploratorio

Benchmark 0.3 no debe iniciar como gate duro. Debe iniciar como benchmark de descubrimiento.

Durante sus primeras ejecuciones debe servir para:

* descubrir fallos;
* crear nuevas métricas;
* identificar puntos débiles;
* comparar métodos;
* diseñar umbrales realistas.

Solo después de dos o tres ejecuciones estables puede convertirse en gate parcial.

---

## 4. Qué no debe bloquear evolución

No debe bloquearse una versión solo porque:

* un benchmark nuevo más difícil baja el score global;
* aparece una métrica nueva que revela fallos antes invisibles;
* un método experimental pierde frente a CPP v1;
* se amplía el corpus a dominios menos favorables;
* se agregan tareas adversariales;
* baja EAS pero mejora seguridad contra claims no soportados;
* baja cobertura global pero mejora preservación P0.

Un benchmark más exigente puede producir scores más bajos y aun así representar avance científico.

---

## 5. Qué sí debe bloquear

Debe bloquearse una versión si ocurre cualquiera de estos casos:

### 5.1 Ruptura de reproducibilidad

El mismo fixture no reproduce resultados previos y no hay cambio declarado.

### 5.2 Violación de presupuesto

Un método excede tokens y aun así se reporta como válido.

### 5.3 Filtración query-dependent

Un método declarado pasivo usa la pregunta o términos de la tarea.

### 5.4 Pérdida de constraints bloqueantes

Una restricción severa desaparece del contexto comprimido y el método permite una acción que debía bloquearse.

### 5.5 Conversión de claim no soportado en hecho

El método promueve como verdad una afirmación declarada tentativa, futura, prohibida o no demostrada.

### 5.6 Mezcla de claims científicos

El informe afirma mejora LLM cuando solo se ejecutó proxy determinístico.

---

## 6. Estrategia recomendada para explicar la regresión 0.1b → 0.2

Antes de tocar CPP, debe ejecutarse una auditoría de regresión en cinco pasos.

### Paso 1 — Congelar fixtures

Crear:

```text
fixture_0_1b/
fixture_0_2/
```

Cada fixture debe incluir corpus, tareas, métodos, scoring, tokenizer y resultados esperados.

### Paso 2 — Ejecutar reproducción cerrada

Ejecutar:

```text
0.1b con harness 0.1b
0.2 con harness 0.2
```

Objetivo:
Confirmar que los resultados originales son reproducibles.

### Paso 3 — Ejecutar reproducción cruzada

Ejecutar:

```text
0.1b con harness actual
0.2 con harness actual
```

Objetivo:
Determinar si la regresión viene del harness o del corpus/tareas.

### Paso 4 — Comparar tarea por tarea

Generar matriz:

```text
task_id
case_id
scenario
budget
score_0_1b
score_0_2
delta
priority_expected
sigil_expected
term_missed
source_missed
failure_type
```

Clasificar cada pérdida como:

```text
missing_P0
missing_constraint
temporal_confusion
source_loss
keyword_mismatch
answer_extraction_error
token_budget_pressure
noise_inclusion
task_changed
gold_changed
```

### Paso 5 — Dictamen

La regresión debe clasificarse como:

```text
real_algorithm_regression
expected_difficulty_increase
harness_regression
metric_regression
corpus_shift
task_design_shift
inconclusive
```

Solo si la mayoría de pérdidas cae en `real_algorithm_regression` se justifica modificar CPP de forma correctiva.

---

## 7. Umbral de regresión recomendado

Mi recomendación concreta:

### Para reproducción histórica

```text
Tolerancia: 0.001
Aplicación: solo fixtures congeladas.
Agresividad: alta.
Justificación: ciencia reproducible.
```

### Para evolución de CPP v1

```text
Tolerancia de alerta: -1.5 pp.
Tolerancia de revisión: -3 pp.
Tolerancia de bloqueo: -5 pp.
Aplicación: Benchmark 0.2 comparable.
Agresividad: media.
Justificación: protege sin congelar.
```

### Para nuevas variantes CPP

```text
No bloquear por no superar CPP v1.
Reportar como método experimental.
Exigir que no viole seguridad, presupuesto ni claims.
Agresividad: baja-media.
Justificación: permite innovación.
```

### Para Benchmark 0.3

```text
Primeras 2 ejecuciones: exploratorio.
Luego: gate parcial por métricas críticas.
No usar score global como bloqueo inicial.
Agresividad: progresiva.
Justificación: evita castigar el descubrimiento empírico.
```

---

## 8. Orden de implementación recomendado

### Fase 1 — Fundación de reproducibilidad

Duración estimada: 1 a 2 semanas.

Entregables:

* fixtures 0.1b y 0.2;
* hashes completos;
* regression_runner.py;
* summary comparator;
* task-level delta report;
* manifest canónico.

No modificar CPP todavía.

### Fase 2 — Diagnóstico de regresión

Duración estimada: 1 semana.

Entregables:

* matriz de fallos por tarea;
* clasificación de causa;
* detección de pérdida P0/P1;
* análisis de ruido por presupuesto;
* explicación del descenso en 4.096 tokens.

No implementar umbrales adaptativos hasta entender si el problema es ruido real.

### Fase 3 — Métricas críticas

Duración estimada: 1 a 2 semanas.

Agregar:

* P0 survival rate;
* P1 survival rate;
* blocking constraint false negatives;
* unsupported claim false positives;
* current/future confusion rate;
* source traceability rate;
* budget violation rate.

Estas métricas deben pesar más que EAS global cuando hay conflicto.

### Fase 4 — CPP adaptativo

Duración estimada: 2 a 4 semanas.

Implementar como método nuevo:

```text
cortex_priority_pack_adaptive_v1
```

No reemplazar CPP original.

Comparar:

```text
CPP original
CPP adaptive
CPP semantic hybrid
positional baselines
query-dependent baseline
```

### Fase 5 — Benchmark 0.3 adversarial

Duración estimada: 2 a 6 semanas.

Debe nacer como benchmark exploratorio, no como gate absoluto.

---

## 9. Criterio de decisión final

La evolución debe aceptarse si cumple:

```text
1. Reproduce fixtures históricas.
2. No viola presupuesto.
3. No mezcla métodos pasivos con query-dependent.
4. No incrementa fallos críticos de seguridad.
5. Explica cualquier caída mayor a 3 puntos.
6. Mejora al menos una dimensión relevante sin destruir otra crítica.
7. Declara sus claims con precisión.
```

La evolución debe rechazarse si:

```text
1. No reproduce lo reproducible.
2. Oculta cambios de corpus, tareas o scoring.
3. Baja métricas críticas sin explicación.
4. Usa benchmarks nuevos para borrar resultados antiguos.
5. Usa resultados determinísticos para afirmar mejora LLM.
6. Sustituye CPP v1 sin conservar comparación histórica.
```

---

## 10. Recomendación ejecutiva

La política correcta para CODEC-CORTEX debe ser:

```text
estricta con la reproducibilidad,
moderada con la evolución,
progresiva con benchmarks nuevos,
dura con claims no soportados,
y muy dura con fallos de seguridad operacional.
```

El punto de regresión sano no es “volver a 0.1b” ni “aceptar todo lo que 0.2 diga”.

El punto sano es:

```text
0.1b como prueba histórica cerrada.
0.2 como baseline operativo comparable.
0.3 como laboratorio adversarial hasta estabilizar métricas.
```

Así se protege la credibilidad científica sin convertir el benchmark en una camisa de fuerza que impida que CODEC-CORTEX evolucione.
