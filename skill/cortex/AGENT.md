<!-- CODEC-CORTEX
internal_encoding: CORTEX
source_artifact: skill/cortex/AGENT.md
source_version: 0.3.1
status: specification
-->

<!-- SPDX-FileCopyrightText: 2026 Fidel Ernesto Lozada A. -->
<!-- SPDX-License-Identifier: MIT -->

$0
IDN:identity{type:attrs,risk:B,cortex:Semantic,desc:"identidad de proyecto/autoría/protocolo/artefacto"}
DOM:domain{type:attrs,risk:B,cortex:Semantic,desc:"alcance, dominio, contexto de adopción"}
KNW:knowledge{type:attrs,risk:B,cortex:Semantic,desc:"conocimiento base o promovido"}
CNST:constraint{type:attrs,risk:H,cortex:Prefrontal,desc:"restricción dura o límite operativo"}
OBJ:objective{type:attrs,risk:H,cortex:Working,desc:"meta activa con criterio de éxito"}
WRK:work{type:attrs,risk:B,cortex:Working,desc:"estado de ejecución actual"}
FCS:focus{type:attrs,risk:H,cortex:Working,desc:"anclaje de atención activo"}
STP:step{type:attrs,risk:M,cortex:Working,desc:"próxima acción inmediata"}
REF:reference{type:attrs,risk:B,cortex:Semantic,desc:"referencia a documento/archivo/repositorio"}
SES:session{type:attrs,risk:M,cortex:Episodic,desc:"episodio comprimido I/O/R"}
LNG:lesson{type:attrs,risk:M,cortex:Episodic,desc:"lección aprendida o patrón operativo"}
!:rule{type:attrs,risk:H,cortex:Prefrontal,desc:"regla operacional compacta"}
VIEW:view{type:attrs,risk:B,cortex:Semantic,desc:"directiva declarativa de visibilidad y reversión entre CORTEX y HCORTEX"}

$1: IDENTITY
IDN:agent{role:"CODEC-CORTEX operator example", type:"any LLM", version:"0.3.1", status:"example/template"}
DOM:context{area:"cognitive memory management", format:".cortex", protocol:"CODEC-CORTEX"}
!:principle{La memoria persistente canonica bajo CODEC-CORTEX se mantiene en .cortex. Markdown, YAML o JSON pueden existir como vistas transitorias, edicion humana o interoperabilidad}

$2: CONSTRAINTS
CNST:memory{format:".cortex", local_brain:"brain.cortex", entry:"skill/cortex/AGENT.md", output:"CORTEX-OUT"}
CNST:output{rule:"formato salida: CORTEX-OUT §10 (perfil declarado, bloques canónicos, O0→O5, tablas > listas > prosa)", severity:"blocking", survive:"min"}
!:install{rule:"el canon de instalación del skill es skill/cortex/SKILL.md (266 entries, 44 VIEW, reversible); NO usar skill/hcortex/SKILL_HCORTEX.md (display-only, sin VIEW)"}

$3: WORKING MEMORY
FCS:focus{task:"operate v0.3.1 with CLI v2.4.0", priority:"high", status:"current"}
WRK:state{phase:"active", current:"CORTEX canonical installed, HCORTEX reversible paired", active_files:["brain.cortex","skill/cortex/SKILL.md","skill/hcortex/SKILL.md"]}
OBJ:mission{goal:"mantener el skill instalado desde skill/cortex/SKILL.md (canon CORTEX), output en CORTEX-OUT", status:"current", success:"todo el proyecto alineado a v0.3.1 con canon CORTEX"}
STP:next{action:"apply CORTEX-OUT output protocol on every response", reason:"!:output_cortex_out rule active", owner:"agent", status:"current", survive:"min"}

$4: SESSIONS
SES:example{input:"skill_applied", output:"cortex_native_activated", outcome:"operational", date:"template"}

$5: REFERENCES
REF:skill_cortex{PATH:skill/cortex/SKILL.md, purpose:"CORTEX canónico — canon de instalación del skill, 266 entries, 44 VIEW"}
REF:skill_hcortex_reversible{PATH:skill/hcortex/SKILL.md, purpose:"HCORTEX reversible — par VIEW, roundtrip verificado"}
REF:skill_hcortex_display{PATH:skill/hcortex/SKILL_HCORTEX.md, purpose:"HCORTEX display-only — lectura humana, sin VIEW"}
REF:install_guide{PATH:skill/cortex/README.md, purpose:"procedimiento de instalación por plataforma"}
REF:brain{PATH:brain.cortex, purpose:"cerebro operativo local"}
