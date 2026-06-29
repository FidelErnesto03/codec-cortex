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
CNST:memory{format:".cortex", local_brain:"brain.cortex", entry:"AGENT.cortex", output:"HCORTEX"}
CNST:output{rule:"formato salida: HCORTEX (tablas > lista > diagramas PUML > prosa)", severity:"blocking", survive:"min"}

$3: WORKING MEMORY
FCS:focus{task:"manage CORTEX contexts", priority:"high", status:"current"}
WRK:state{phase:"active", current:"aligned to SKILL_HCORTEX.md v1.2.0", active_files:["brain.cortex","skill/cortex/SKILL.md","skill/hcortex/SKILL_HCORTEX.md"]}
OBJ:mission{goal:"mantener alineación del proyecto al canon SKILL_HCORTEX.md", status:"current", success:"todo el proyecto alineado excepto CLI"}

$4: SESSIONS
SES:example{input:"skill_applied", output:"cortex_native_activated", outcome:"operational", date:"template"}

$5: REFERENCES
REF:skill_cortex{PATH:skill/cortex/SKILL.md, purpose:"mente CORTEX del protocolo"}
REF:skill_hcortex{PATH:skill/hcortex/SKILL_HCORTEX.md, purpose:"canon HCORTEX vigente"}
REF:brain{PATH:brain.cortex, purpose:"cerebro operativo local"}
