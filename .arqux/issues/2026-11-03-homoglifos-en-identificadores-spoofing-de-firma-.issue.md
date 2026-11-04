# ISSUE: Homoglifos en identificadores: spoofing de firma via nombres unicode (D2b NEX)
# Severity: high | Status: fixed | Handler: alfred | Date: 2026-11-03

## PROBLEM
Hallazgo nuevo de la segunda oleada de Lokky (docs/EXTERNAL-REVIEW-NEX-2026-11-C2.md par.3), verificado localmente. Vector: dos nombres de idea visualmente identicos pero distintos a nivel byte — USR:admin (a latina U+0061) vs USR:\u0430dmin (a cirilica U+0430) — parsean como ideas distintas, I006 no dispara (direcciones difieren en bytes), y el render HCORTEX muestra dos '### USR:admin' identicos. Clase: spoofing de identificador — un manifiesto puede colar una segunda entidad visualmente identica a la aprobada; el humano firma lo que ve y lo que ve miente (analogo al phishing IDN). Superficie expuesta: nombres de idea (regex [^{|}\\s]+ sin charset) y claves de attrs (lectura sin charset) en ambos dialectos; sigilos [A-Z0-9_] y namespaces [a-z0-9_.-] ya son ASCII. HOMOGLYPHS/detect_homoglyph existe en slots.py:27,67 pero solo aplica al marcador. Contexto: C14N-0.1 ya declara identificadores estructurales restringidos a ASCII — promesa sin emisor, misma clase que enum/I007. Radio de impacto de ASCII-estricto: CERO — 0 nombres no-ASCII en corpus+.arqux. Decision pendiente del Arquitecto: (a) restringir identificadores a ASCII imprimible [simple, deterministico, consistente con spec 0.1] o (b) extender detect_homoglyph a nombres+claves con diagnostico U0xx_CONFUSABLE_IDENTIFIER [mas permisivo, requiere tabla de confusables]. Contenido (text/cuerpo/bloque) queda unicode libre en ambas.

## CONTEXT
reported_by: Alfred
reported_at: 2026-11-03T23:49:45Z

## LESSON
cause:      pending triage
fix:        pending triage
prevention: pending triage

## UPDATE 2026-11-03

Opcion A implementada (decision Arquitecto): identificadores estructurales = ASCII imprimible, diagnostico U003_NON_ASCII_IDENTIFIER en scalars.py/parser.py/slotparser.py (nombre idea, claves attrs, label sigilo, nombre $0, campo contrato); enum values exigen gramatica atom (G014). Vector I_U003_homoglyph_name en slots. Regresion: corpus 364/364, slots 68/68. Contenido Unicode libre. Spec S4.4 nuevo + catalogos errors. Pendiente port go/node/rs/bash bajo issue port-fixes.
