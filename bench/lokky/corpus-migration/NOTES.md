# Migración corpus → identificadores ASCII (post-U003)

Hallazgo: el corpus sellado `formats/cortex.cortex` rompe bajo el parser endurecido
(`U003_NON_ASCII_IDENTIFIER @ 14:0`) — dos nombres de idea llevan tilde:
- EQP:Lucía_Rojas{rol:"Platform Engineer",proyectos:["Horizon","Aegis"],seniority:7,activo:t
- EQP:Sofía_Márquez{rol:"DevOps Lead",proyectos:["Nebula","Aegis","Phoenix"],seniority:8,act

Fix aplicado aquí: transliterar SOLO la posición de nombre de idea
(`Lucía_Rojas`→`Lucia_Rojas`, `Sofía_Márquez`→`Sofia_Marquez`). El contenido
(texto de campos) conserva unicode libre — `prioridad:"crítica"` etc. intacto.

Impacto en scoring: NULO — `scorer.py::norm()` ya normaliza NFKD, así que
`Sofia_Marquez` y `Sofía_Márquez` puntúan igual contra GOLD.

Estado: parse OK 1.0 | 40 ideas
Decisión pendiente del Arquitecto: adoptar este archivo como corpus sellado
nuevo (re-sellar SHA256SUMS) o mantener el viejo para lectura 0.1/legacy.
