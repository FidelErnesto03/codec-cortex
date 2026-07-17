$0
$0:format{cortex:0.1,encoding:UTF-8,language:es,type:benchmark}
TST:task{type:attrs,weight:H,fields:"id:text|question:text|type:%qtype|requires:text",focus:question,schema:table,desc:"Pregunta del benchmark"}
FMT:format{type:attrs,weight:H,fields:"name:text|chars:number|tokens:number|precision:text",focus:name,schema:table,desc:"Resultado por formato"}
MTR:metric{type:attrs,weight:H,fields:"name:text|format:text|value:text",focus:value,schema:table,desc:"Metrica"}
CTX:context{type:cuerpo,weight:M,schema:prose,desc:"Contexto del escenario"}
$1: ESCENARIO
CTX:context{Eres el agente de operaciones de "NexusCorp", una empresa de infraestructura cloud con 200 empleados. Tu knowledge base contiene información estructurada sobre: equipo (8 miembros), proyectos activos (5), dependencias entre proyectos (7), riesgos identificados (6), decisiones de arquitectura (5), incidentes recientes (4), y proveedores (5). Esta información está duplicada en 6 formatos distintos. Tu tarea es responder 8 preguntas usando CADA formato, y comparar cuál fue más eficiente.}
$2: PROTOCOLO
TST:task{id:"PROTO-1",question:"Lee TODA la información en §4 (los 6 formatos). Contiene los mismos datos — 40 entradas en total — presentadas en CORTEX, JSON, YAML, Markdown, texto plano y XML.",type:instruccion,requires:"§4"}
TST:task{id:"PROTO-2",question:"Responde las 8 preguntas de §5. Para CADA pregunta, debes responderla 6 VECES — una por cada formato. Es decir, 48 respuestas en total.",type:instruccion,requires:"§5"}
TST:task{id:"PROTO-3",question:"Para cada pregunta-formato, anota: ¿fue posible responder? (sí/no), ¿cuántos tokens del prompt inspeccionaste mentalmente para encontrar la respuesta? (estima), y la respuesta extraída.",type:instruccion,requires:"§5"}
TST:task{id:"PROTO-4",question:"Al finalizar, emite un reporte en el formato de §6: una tabla comparativa con los 6 formatos × 8 preguntas + métricas agregadas.",type:instruccion,requires:"§6"}
$3: PREGUNTAS DE ALTO ESTRÉS
TST:task{id:"Q1",question:"¿Quién es el responsable del proyecto 'Nebula' y cuál es su fecha límite?",type:simple,requires:"una sección"}
TST:task{id:"Q2",question:"¿Qué riesgos afectan al proyecto con deadline más cercano? Lista todos.",type:multi-seccion,requires:"dos secciones"}
TST:task{id:"Q3",question:"¿Qué proveedor fue responsable del incidente I-004 y qué decisión arquitectónica se tomó como consecuencia?",type:multi-hop,requires:"tres secciones"}
TST:task{id:"Q4",question:"¿Cuántos miembros del equipo trabajan en más de un proyecto simultáneamente? Nómbralos.",type:agregacion,requires:"dos secciones"}
TST:task{id:"Q5",question:"¿Qué riesgo tiene el nivel de impacto más alto (crítico) y qué proyecto y proveedor están asociados a él?",type:multi-hop-profundo,requires:"tres secciones"}
TST:task{id:"Q6",question:"Del incidente más reciente: ¿qué dependencia entre proyectos se vio afectada y qué decisión se tomó para mitigarlo?",type:causal,requires:"tres secciones"}
TST:task{id:"Q7",question:"¿Hay algún riesgo que afecte a MÚLTIPLES proyectos simultáneamente? Si es así, ¿qué proyectos y qué proveedores están en la cadena de impacto?",type:transversal,requires:"cuatro secciones"}
TST:task{id:"Q8",question:"Basado en TODA la información disponible, ¿cuál es el proyecto en mayor peligro? Justifica tu respuesta citando riesgos, dependencias, incidentes y decisiones que lo afectan.",type:sintesis,requires:"cinco secciones"}
$4: DATOS — Mismos 40 items en 6 formatos
# §4: DATOS — Mismos 40 items en 6 formatos

> **NexusCorp Knowledge Base** — 8 team + 5 projects + 7 dependencies + 6 risks + 5 decisions + 4 incidents + 5 providers = **40 items total**
> Cada formato contiene EXACTAMENTE la misma información. El benchmark mide cuál formato permite responder más rápido y con mayor precisión.

---

## Formato 1: CORTEX 0.1

```
$0
$0:format{cortex:0.1,encoding:UTF-8,entity:NexusCorp,domain:infraestructura-cloud}

$N: EQUIPO (8 miembros)
EQP:Elena_Vargas{rol:"Arquitecta Cloud",proyectos:["Nebula","Horizon"],seniority:12,activo:true}
EQP:Marco_Silva{rol:"SRE Lead",proyectos:["Nebula"],seniority:9,activo:true}
EQP:Lucía_Rojas{rol:"Platform Engineer",proyectos:["Horizon","Aegis"],seniority:7,activo:true}
EQP:Daniel_Ortega{rol:"Security Lead",proyectos:["Aegis","Phoenix"],seniority:11,activo:true}
EQP:Aisha_Okafor{rol:"Data Engineer",proyectos:["Nebula","Phoenix"],seniority:6,activo:true}
EQP:Chen_Wei{rol:"Network Architect",proyectos:["Horizon"],seniority:14,activo:true}
EQP:Sofía_Márquez{rol:"DevOps Lead",proyectos:["Nebula","Aegis","Phoenix"],seniority:8,activo:true}
EQP:Liam_O'Connor{rol:"Backend Engineer",proyectos:["Aegis"],seniority:4,activo:true}

$N: PROYECTOS (5)
PRJ:Nebula{id:"T01",deadline:"2026-09-15",presupuesto:850000,prioridad:"alta",estado:"activo"}
PRJ:Horizon{id:"T03",deadline:"2026-08-01",presupuesto:420000,prioridad:"media",estado:"activo"}
PRJ:Aegis{id:"T07",deadline:"2027-01-10",presupuesto:1200000,prioridad:"crítica",estado:"activo"}
PRJ:Phoenix{id:"T04",deadline:"2026-10-30",presupuesto:670000,prioridad:"alta",estado:"activo"}
PRJ:Atlas{id:"T06",deadline:"2026-07-30",presupuesto:300000,prioridad:"baja",estado:"activo"}

$N: DEPENDENCIAS (7)
DEP:D01{origen:"Horizon",destino:"Nebula",tipo:"bloqueante",desc:"Horizon bloquea a Nebula"}
DEP:D02{origen:"Nebula",destino:"Aegis",tipo:"dependencia",desc:"Nebula depende de Aegis"}
DEP:D03{origen:"Phoenix",destino:"Aegis",tipo:"dependencia",desc:"Phoenix depende de Aegis"}
DEP:D04{origen:"Aegis",destino:"Phoenix",tipo:"bloqueante",desc:"Aegis bloquea a Phoenix"}
DEP:D05{origen:"Atlas",destino:"Horizon",tipo:"legado",desc:"Atlas depende de Horizon (legado)"}
DEP:D06{origen:"Nebula",destino:"Phoenix",tipo:"dependencia",desc:"Nebula depende de Phoenix"}
DEP:D07{origen:"Horizon",destino:"Aegis",tipo:"bloqueante",desc:"Horizon bloquea a Aegis"}

$N: RIESGOS (6)
RSK:R01{desc:"Fuga de datos en API Gateway",impacto:"crítico",proyectos:["Horizon","Nebula"],proveedor:"CloudShield",probabilidad:0.35}
RSK:R02{desc:"Incumplimiento de deadline de Nebula",impacto:"alto",proyectos:["Nebula"],proveedor:"N/A",probabilidad:0.60}
RSK:R03{desc:"Rotación de Sofía Márquez",impacto:"alto",proyectos:["Aegis","Nebula","Phoenix"],proveedor:"N/A",probabilidad:0.45}
RSK:R04{desc:"Zero-day en motor de eventos",impacto:"crítico",proyectos:["Nebula","Phoenix"],proveedor:"StreamCore",probabilidad:0.20}
RSK:R05{desc:"Sobrecoste de DataVault",impacto:"medio",proyectos:["Aegis"],proveedor:"DataVault",probabilidad:0.55}
RSK:R06{desc:"Incumplimiento de compliance en Phoenix",impacto:"alto",proyectos:["Phoenix"],proveedor:"ComplianceAudit",probabilidad:0.40}

$N: DECISIONES DE ARQUITECTURA (5)
DEC:AR01{desc:"Adopción de Kubernetes como plataforma de orquestación",trimestre:"T01",proyectos:["Nebula","Horizon","Aegis"],post_incidente:"N/A"}
DEC:AR02{desc:"Migración a OAuth2 para autenticación de servicios",trimestre:"T04",proyectos:["Aegis","Phoenix"],post_incidente:"I-004"}
DEC:AR03{desc:"Arquitectura de motor de eventos desacoplado",trimestre:"T01",proyectos:["Nebula","Phoenix"],post_incidente:"I-002"}
DEC:AR04{desc:"Rotación automática de secretos cada 72h",trimestre:"T04",proyectos:["Nebula","Horizon","Aegis","Phoenix","Atlas"],post_incidente:"R01,R04"}
DEC:AR05{desc:"Redundancia geográfica de DataVault",trimestre:"T07",proyectos:["Aegis"],post_incidente:"R05"}

$N: INCIDENTES (4)
INC:I-001{desc:"Latencia crítica en API Gateway de Horizon",fecha:"2026-06-15",severidad:"alta",proveedor:"CloudShield",estado:"resuelto",duracion_h:4.5}
INC:I-002{desc:"Pérdida de eventos en el bus de Nebula",fecha:"2026-06-22",severidad:"media",proveedor:"StreamCore",estado:"resuelto",duracion_h:2.0}
INC:I-003{desc:"Caducidad de certificado TLS en Atlas",fecha:"2026-07-01",severidad:"baja",proveedor:"CloudShield",estado:"resuelto",duracion_h:1.0}
INC:I-004{desc:"Fuga de tokens de acceso en Aegis",fecha:"2026-07-10",severidad:"crítica",proveedor:"ComplianceAudit",estado:"no_resuelto",duracion_h:0.0}

$N: PROVEEDORES (5)
PRV:CloudShield{servicio:"WAF + API Gateway",costo_mensual:15000,proyectos:["Horizon","Nebula"],sla:"99.99%"}
PRV:StreamCore{servicio:"Event Bus",costo_mensual:8200,proyectos:["Nebula","Phoenix"],sla:"99.95%"}
PRV:DataVault{servicio:"S3 Storage",costo_mensual:23000,proyectos:["Aegis"],sla:"99.99%"}
PRV:ComplianceAudit{servicio:"SOC2 Compliance",costo_mensual:18000,proyectos:["Phoenix"],sla:"99.90%"}
PRV:NetScale{servicio:"CDN + DNS",costo_mensual:9500,proyectos:["Nebula","Horizon","Phoenix"],sla:"99.99%"}
```

---

## Formato 2: JSON

```json
{
  "nexuscorp_kb": {
    "equipo": [
      {
        "id": "Elena_Vargas",
        "rol": "Arquitecta Cloud",
        "proyectos": ["Nebula", "Horizon"],
        "seniority": 12,
        "activo": true
      },
      {
        "id": "Marco_Silva",
        "rol": "SRE Lead",
        "proyectos": ["Nebula"],
        "seniority": 9,
        "activo": true
      },
      {
        "id": "Lucía_Rojas",
        "rol": "Platform Engineer",
        "proyectos": ["Horizon", "Aegis"],
        "seniority": 7,
        "activo": true
      },
      {
        "id": "Daniel_Ortega",
        "rol": "Security Lead",
        "proyectos": ["Aegis", "Phoenix"],
        "seniority": 11,
        "activo": true
      },
      {
        "id": "Aisha_Okafor",
        "rol": "Data Engineer",
        "proyectos": ["Nebula", "Phoenix"],
        "seniority": 6,
        "activo": true
      },
      {
        "id": "Chen_Wei",
        "rol": "Network Architect",
        "proyectos": ["Horizon"],
        "seniority": 14,
        "activo": true
      },
      {
        "id": "Sofía_Márquez",
        "rol": "DevOps Lead",
        "proyectos": ["Nebula", "Aegis", "Phoenix"],
        "seniority": 8,
        "activo": true
      },
      {
        "id": "Liam_O'Connor",
        "rol": "Backend Engineer",
        "proyectos": ["Aegis"],
        "seniority": 4,
        "activo": true
      }
    ],
    "proyectos": [
      {
        "id": "Nebula",
        "codigo": "T01",
        "deadline": "2026-09-15",
        "presupuesto": 850000,
        "prioridad": "alta",
        "estado": "activo"
      },
      {
        "id": "Horizon",
        "codigo": "T03",
        "deadline": "2026-08-01",
        "presupuesto": 420000,
        "prioridad": "media",
        "estado": "activo"
      },
      {
        "id": "Aegis",
        "codigo": "T07",
        "deadline": "2027-01-10",
        "presupuesto": 1200000,
        "prioridad": "crítica",
        "estado": "activo"
      },
      {
        "id": "Phoenix",
        "codigo": "T04",
        "deadline": "2026-10-30",
        "presupuesto": 670000,
        "prioridad": "alta",
        "estado": "activo"
      },
      {
        "id": "Atlas",
        "codigo": "T06",
        "deadline": "2026-07-30",
        "presupuesto": 300000,
        "prioridad": "baja",
        "estado": "activo"
      }
    ],
    "dependencias": [
      {
        "id": "D01",
        "origen": "Horizon",
        "destino": "Nebula",
        "tipo": "bloqueante",
        "descripcion": "Horizon bloquea a Nebula"
      },
      {
        "id": "D02",
        "origen": "Nebula",
        "destino": "Aegis",
        "tipo": "dependencia",
        "descripcion": "Nebula depende de Aegis"
      },
      {
        "id": "D03",
        "origen": "Phoenix",
        "destino": "Aegis",
        "tipo": "dependencia",
        "descripcion": "Phoenix depende de Aegis"
      },
      {
        "id": "D04",
        "origen": "Aegis",
        "destino": "Phoenix",
        "tipo": "bloqueante",
        "descripcion": "Aegis bloquea a Phoenix"
      },
      {
        "id": "D05",
        "origen": "Atlas",
        "destino": "Horizon",
        "tipo": "legado",
        "descripcion": "Atlas depende de Horizon (legado)"
      },
      {
        "id": "D06",
        "origen": "Nebula",
        "destino": "Phoenix",
        "tipo": "dependencia",
        "descripcion": "Nebula depende de Phoenix"
      },
      {
        "id": "D07",
        "origen": "Horizon",
        "destino": "Aegis",
        "tipo": "bloqueante",
        "descripcion": "Horizon bloquea a Aegis"
      }
    ],
    "riesgos": [
      {
        "id": "R01",
        "descripcion": "Fuga de datos en API Gateway",
        "impacto": "crítico",
        "proyectos": ["Horizon", "Nebula"],
        "proveedor": "CloudShield",
        "probabilidad": 0.35
      },
      {
        "id": "R02",
        "descripcion": "Incumplimiento de deadline de Nebula",
        "impacto": "alto",
        "proyectos": ["Nebula"],
        "proveedor": null,
        "probabilidad": 0.60
      },
      {
        "id": "R03",
        "descripcion": "Rotación de Sofía Márquez",
        "impacto": "alto",
        "proyectos": ["Aegis", "Nebula", "Phoenix"],
        "proveedor": null,
        "probabilidad": 0.45
      },
      {
        "id": "R04",
        "descripcion": "Zero-day en motor de eventos",
        "impacto": "crítico",
        "proyectos": ["Nebula", "Phoenix"],
        "proveedor": "StreamCore",
        "probabilidad": 0.20
      },
      {
        "id": "R05",
        "descripcion": "Sobrecoste de DataVault",
        "impacto": "medio",
        "proyectos": ["Aegis"],
        "proveedor": "DataVault",
        "probabilidad": 0.55
      },
      {
        "id": "R06",
        "descripcion": "Incumplimiento de compliance en Phoenix",
        "impacto": "alto",
        "proyectos": ["Phoenix"],
        "proveedor": "ComplianceAudit",
        "probabilidad": 0.40
      }
    ],
    "decisiones": [
      {
        "id": "AR01",
        "descripcion": "Adopción de Kubernetes como plataforma de orquestación",
        "trimestre": "T01",
        "proyectos": ["Nebula", "Horizon", "Aegis"],
        "post_incidente": null
      },
      {
        "id": "AR02",
        "descripcion": "Migración a OAuth2 para autenticación de servicios",
        "trimestre": "T04",
        "proyectos": ["Aegis", "Phoenix"],
        "post_incidente": "I-004"
      },
      {
        "id": "AR03",
        "descripcion": "Arquitectura de motor de eventos desacoplado",
        "trimestre": "T01",
        "proyectos": ["Nebula", "Phoenix"],
        "post_incidente": "I-002"
      },
      {
        "id": "AR04",
        "descripcion": "Rotación automática de secretos cada 72h",
        "trimestre": "T04",
        "proyectos": ["Nebula", "Horizon", "Aegis", "Phoenix", "Atlas"],
        "post_incidente": "R01,R04"
      },
      {
        "id": "AR05",
        "descripcion": "Redundancia geográfica de DataVault",
        "trimestre": "T07",
        "proyectos": ["Aegis"],
        "post_incidente": "R05"
      }
    ],
    "incidentes": [
      {
        "id": "I-001",
        "descripcion": "Latencia crítica en API Gateway de Horizon",
        "fecha": "2026-06-15",
        "severidad": "alta",
        "proveedor": "CloudShield",
        "estado": "resuelto",
        "duracion_horas": 4.5
      },
      {
        "id": "I-002",
        "descripcion": "Pérdida de eventos en el bus de Nebula",
        "fecha": "2026-06-22",
        "severidad": "media",
        "proveedor": "StreamCore",
        "estado": "resuelto",
        "duracion_horas": 2.0
      },
      {
        "id": "I-003",
        "descripcion": "Caducidad de certificado TLS en Atlas",
        "fecha": "2026-07-01",
        "severidad": "baja",
        "proveedor": "CloudShield",
        "estado": "resuelto",
        "duracion_horas": 1.0
      },
      {
        "id": "I-004",
        "descripcion": "Fuga de tokens de acceso en Aegis",
        "fecha": "2026-07-10",
        "severidad": "crítica",
        "proveedor": "ComplianceAudit",
        "estado": "no_resuelto",
        "duracion_horas": null
      }
    ],
    "proveedores": [
      {
        "id": "CloudShield",
        "servicio": "WAF + API Gateway",
        "costo_mensual": 15000,
        "proyectos": ["Horizon", "Nebula"],
        "sla": "99.99%"
      },
      {
        "id": "StreamCore",
        "servicio": "Event Bus",
        "costo_mensual": 8200,
        "proyectos": ["Nebula", "Phoenix"],
        "sla": "99.95%"
      },
      {
        "id": "DataVault",
        "servicio": "S3 Storage",
        "costo_mensual": 23000,
        "proyectos": ["Aegis"],
        "sla": "99.99%"
      },
      {
        "id": "ComplianceAudit",
        "servicio": "SOC2 Compliance",
        "costo_mensual": 18000,
        "proyectos": ["Phoenix"],
        "sla": "99.90%"
      },
      {
        "id": "NetScale",
        "servicio": "CDN + DNS",
        "costo_mensual": 9500,
        "proyectos": ["Nebula", "Horizon", "Phoenix"],
        "sla": "99.99%"
      }
    ]
  }
}
```

---

## Formato 3: YAML

```yaml
nexuscorp_kb:
  equipo:
    - id: Elena_Vargas
      rol: Arquitecta Cloud
      proyectos:
        - Nebula
        - Horizon
      seniority: 12
      activo: true
    - id: Marco_Silva
      rol: SRE Lead
      proyectos:
        - Nebula
      seniority: 9
      activo: true
    - id: Lucía_Rojas
      rol: Platform Engineer
      proyectos:
        - Horizon
        - Aegis
      seniority: 7
      activo: true
    - id: Daniel_Ortega
      rol: Security Lead
      proyectos:
        - Aegis
        - Phoenix
      seniority: 11
      activo: true
    - id: Aisha_Okafor
      rol: Data Engineer
      proyectos:
        - Nebula
        - Phoenix
      seniority: 6
      activo: true
    - id: Chen_Wei
      rol: Network Architect
      proyectos:
        - Horizon
      seniority: 14
      activo: true
    - id: Sofía_Márquez
      rol: DevOps Lead
      proyectos:
        - Nebula
        - Aegis
        - Phoenix
      seniority: 8
      activo: true
    - id: Liam_O'Connor
      rol: Backend Engineer
      proyectos:
        - Aegis
      seniority: 4
      activo: true

  proyectos:
    - id: Nebula
      codigo: T01
      deadline: "2026-09-15"
      presupuesto: 850000
      prioridad: alta
      estado: activo
    - id: Horizon
      codigo: T03
      deadline: "2026-08-01"
      presupuesto: 420000
      prioridad: media
      estado: activo
    - id: Aegis
      codigo: T07
      deadline: "2027-01-10"
      presupuesto: 1200000
      prioridad: crítica
      estado: activo
    - id: Phoenix
      codigo: T04
      deadline: "2026-10-30"
      presupuesto: 670000
      prioridad: alta
      estado: activo
    - id: Atlas
      codigo: T06
      deadline: "2026-07-30"
      presupuesto: 300000
      prioridad: baja
      estado: activo

  dependencias:
    - id: D01
      origen: Horizon
      destino: Nebula
      tipo: bloqueante
      descripcion: Horizon bloquea a Nebula
    - id: D02
      origen: Nebula
      destino: Aegis
      tipo: dependencia
      descripcion: Nebula depende de Aegis
    - id: D03
      origen: Phoenix
      destino: Aegis
      tipo: dependencia
      descripcion: Phoenix depende de Aegis
    - id: D04
      origen: Aegis
      destino: Phoenix
      tipo: bloqueante
      descripcion: Aegis bloquea a Phoenix
    - id: D05
      origen: Atlas
      destino: Horizon
      tipo: legado
      descripcion: Atlas depende de Horizon (legado)
    - id: D06
      origen: Nebula
      destino: Phoenix
      tipo: dependencia
      descripcion: Nebula depende de Phoenix
    - id: D07
      origen: Horizon
      destino: Aegis
      tipo: bloqueante
      descripcion: Horizon bloquea a Aegis

  riesgos:
    - id: R01
      descripcion: Fuga de datos en API Gateway
      impacto: crítico
      proyectos:
        - Horizon
        - Nebula
      proveedor: CloudShield
      probabilidad: 0.35
    - id: R02
      descripcion: Incumplimiento de deadline de Nebula
      impacto: alto
      proyectos:
        - Nebula
      proveedor: ~
      probabilidad: 0.60
    - id: R03
      descripcion: Rotación de Sofía Márquez
      impacto: alto
      proyectos:
        - Aegis
        - Nebula
        - Phoenix
      proveedor: ~
      probabilidad: 0.45
    - id: R04
      descripcion: Zero-day en motor de eventos
      impacto: crítico
      proyectos:
        - Nebula
        - Phoenix
      proveedor: StreamCore
      probabilidad: 0.20
    - id: R05
      descripcion: Sobrecoste de DataVault
      impacto: medio
      proyectos:
        - Aegis
      proveedor: DataVault
      probabilidad: 0.55
    - id: R06
      descripcion: Incumplimiento de compliance en Phoenix
      impacto: alto
      proyectos:
        - Phoenix
      proveedor: ComplianceAudit
      probabilidad: 0.40

  decisiones:
    - id: AR01
      descripcion: Adopción de Kubernetes como plataforma de orquestación
      trimestre: T01
      proyectos:
        - Nebula
        - Horizon
        - Aegis
      post_incidente: ~
    - id: AR02
      descripcion: Migración a OAuth2 para autenticación de servicios
      trimestre: T04
      proyectos:
        - Aegis
        - Phoenix
      post_incidente: I-004
    - id: AR03
      descripcion: Arquitectura de motor de eventos desacoplado
      trimestre: T01
      proyectos:
        - Nebula
        - Phoenix
      post_incidente: I-002
    - id: AR04
      descripcion: Rotación automática de secretos cada 72h
      trimestre: T04
      proyectos:
        - Nebula
        - Horizon
        - Aegis
        - Phoenix
        - Atlas
      post_incidente: R01,R04
    - id: AR05
      descripcion: Redundancia geográfica de DataVault
      trimestre: T07
      proyectos:
        - Aegis
      post_incidente: R05

  incidentes:
    - id: I-001
      descripcion: Latencia crítica en API Gateway de Horizon
      fecha: "2026-06-15"
      severidad: alta
      proveedor: CloudShield
      estado: resuelto
      duracion_horas: 4.5
    - id: I-002
      descripcion: Pérdida de eventos en el bus de Nebula
      fecha: "2026-06-22"
      severidad: media
      proveedor: StreamCore
      estado: resuelto
      duracion_horas: 2.0
    - id: I-003
      descripcion: Caducidad de certificado TLS en Atlas
      fecha: "2026-07-01"
      severidad: baja
      proveedor: CloudShield
      estado: resuelto
      duracion_horas: 1.0
    - id: I-004
      descripcion: Fuga de tokens de acceso en Aegis
      fecha: "2026-07-10"
      severidad: crítica
      proveedor: ComplianceAudit
      estado: no_resuelto
      duracion_horas: ~

  proveedores:
    - id: CloudShield
      servicio: WAF + API Gateway
      costo_mensual: 15000
      proyectos:
        - Horizon
        - Nebula
      sla: "99.99%"
    - id: StreamCore
      servicio: Event Bus
      costo_mensual: 8200
      proyectos:
        - Nebula
        - Phoenix
      sla: "99.95%"
    - id: DataVault
      servicio: S3 Storage
      costo_mensual: 23000
      proyectos:
        - Aegis
      sla: "99.99%"
    - id: ComplianceAudit
      servicio: SOC2 Compliance
      costo_mensual: 18000
      proyectos:
        - Phoenix
      sla: "99.90%"
    - id: NetScale
      servicio: CDN + DNS
      costo_mensual: 9500
      proyectos:
        - Nebula
        - Horizon
        - Phoenix
      sla: "99.99%"
```

---

## Formato 4: Markdown Tables

### Equipo (8 miembros)

| ID | Nombre | Rol | Proyectos | Seniority | Activo |
|----|--------|-----|-----------|-----------|--------|
| EQP-01 | Elena Vargas | Arquitecta Cloud | Nebula, Horizon | 12 | ✅ |
| EQP-02 | Marco Silva | SRE Lead | Nebula | 9 | ✅ |
| EQP-03 | Lucía Rojas | Platform Engineer | Horizon, Aegis | 7 | ✅ |
| EQP-04 | Daniel Ortega | Security Lead | Aegis, Phoenix | 11 | ✅ |
| EQP-05 | Aisha Okafor | Data Engineer | Nebula, Phoenix | 6 | ✅ |
| EQP-06 | Chen Wei | Network Architect | Horizon | 14 | ✅ |
| EQP-07 | Sofía Márquez | DevOps Lead | Nebula, Aegis, Phoenix | 8 | ✅ |
| EQP-08 | Liam O'Connor | Backend Engineer | Aegis | 4 | ✅ |

### Proyectos (5)

| ID | Código | Nombre | Deadline | Presupuesto | Prioridad | Estado |
|----|--------|--------|----------|-------------|-----------|--------|
| PRJ-01 | T01 | Nebula | 2026-09-15 | $850,000 | Alta | Activo |
| PRJ-02 | T03 | Horizon | 2026-08-01 | $420,000 | Media | Activo |
| PRJ-03 | T07 | Aegis | 2027-01-10 | $1,200,000 | Crítica | Activo |
| PRJ-04 | T04 | Phoenix | 2026-10-30 | $670,000 | Alta | Activo |
| PRJ-05 | T06 | Atlas | 2026-07-30 | $300,000 | Baja | Activo |

### Dependencias (7)

| ID | Origen | Destino | Tipo | Descripción |
|----|--------|---------|------|-------------|
| D01 | Horizon | Nebula | Bloqueante | Horizon bloquea a Nebula |
| D02 | Nebula | Aegis | Dependencia | Nebula depende de Aegis |
| D03 | Phoenix | Aegis | Dependencia | Phoenix depende de Aegis |
| D04 | Aegis | Phoenix | Bloqueante | Aegis bloquea a Phoenix |
| D05 | Atlas | Horizon | Legado | Atlas depende de Horizon (legado) |
| D06 | Nebula | Phoenix | Dependencia | Nebula depende de Phoenix |
| D07 | Horizon | Aegis | Bloqueante | Horizon bloquea a Aegis |

### Riesgos (6)

| ID | Descripción | Impacto | Proyectos afectados | Proveedor | Probabilidad |
|----|-------------|---------|---------------------|-----------|-------------|
| R01 | Fuga de datos en API Gateway | 🔴 Crítico | Horizon, Nebula | CloudShield | 35% |
| R02 | Incumplimiento de deadline de Nebula | 🟠 Alto | Nebula | N/A | 60% |
| R03 | Rotación de Sofía Márquez | 🟠 Alto | Aegis, Nebula, Phoenix | N/A | 45% |
| R04 | Zero-day en motor de eventos | 🔴 Crítico | Nebula, Phoenix | StreamCore | 20% |
| R05 | Sobrecoste de DataVault | 🟡 Medio | Aegis | DataVault | 55% |
| R06 | Incumplimiento de compliance en Phoenix | 🟠 Alto | Phoenix | ComplianceAudit | 40% |

### Decisiones de Arquitectura (5)

| ID | Descripción | Trimestre | Proyectos | Post-incidente |
|----|-------------|-----------|-----------|----------------|
| AR01 | Adopción de Kubernetes como plataforma de orquestación | T01 | Nebula, Horizon, Aegis | — |
| AR02 | Migración a OAuth2 para autenticación de servicios | T04 | Aegis, Phoenix | I-004 |
| AR03 | Arquitectura de motor de eventos desacoplado | T01 | Nebula, Phoenix | I-002 |
| AR04 | Rotación automática de secretos cada 72h | T04 | Nebula, Horizon, Aegis, Phoenix, Atlas | R01, R04 |
| AR05 | Redundancia geográfica de DataVault | T07 | Aegis | R05 |

### Incidentes (4)

| ID | Descripción | Fecha | Severidad | Proveedor | Estado | Duración (h) |
|----|-------------|-------|-----------|-----------|--------|-------------|
| I-001 | Latencia crítica en API Gateway de Horizon | 2026-06-15 | Alta | CloudShield | ✅ Resuelto | 4.5 |
| I-002 | Pérdida de eventos en el bus de Nebula | 2026-06-22 | Media | StreamCore | ✅ Resuelto | 2.0 |
| I-003 | Caducidad de certificado TLS en Atlas | 2026-07-01 | Baja | CloudShield | ✅ Resuelto | 1.0 |
| I-004 | Fuga de tokens de acceso en Aegis | 2026-07-10 | 🔴 Crítica | ComplianceAudit | ❌ No resuelto | — |

### Proveedores (5)

| ID | Servicio | Costo mensual | Proyectos | SLA |
|----|----------|---------------|-----------|-----|
| CloudShield | WAF + API Gateway | $15,000 | Horizon, Nebula | 99.99% |
| StreamCore | Event Bus | $8,200 | Nebula, Phoenix | 99.95% |
| DataVault | S3 Storage | $23,000 | Aegis | 99.99% |
| ComplianceAudit | SOC2 Compliance | $18,000 | Phoenix | 99.90% |
| NetScale | CDN + DNS | $9,500 | Nebula, Horizon, Phoenix | 99.99% |

---

## Formato 5: Plain Text (Natural Language)

```
NEXUSCORP — KNOWLEDGE BASE COMPLETA
====================================

EQUIPO (8 miembros)
-------------------
1. Elena Vargas es Arquitecta Cloud con 12 años de seniority. Trabaja en los proyectos Nebula y Horizon. Está activa.

2. Marco Silva es SRE Lead con 9 años de seniority. Trabaja exclusivamente en el proyecto Nebula. Está activo.

3. Lucía Rojas es Platform Engineer con 7 años de seniority. Trabaja en los proyectos Horizon y Aegis. Está activa.

4. Daniel Ortega es Security Lead con 11 años de seniority. Trabaja en los proyectos Aegis y Phoenix. Está activo.

5. Aisha Okafor es Data Engineer con 6 años de seniority. Trabaja en los proyectos Nebula y Phoenix. Está activa.

6. Chen Wei es Network Architect con 14 años de seniority — el miembro más experimentado del equipo. Trabaja exclusivamente en Horizon. Está activo.

7. Sofía Márquez es DevOps Lead con 8 años de seniority. Es la persona con mayor carga de proyectos: Nebula, Aegis y Phoenix simultáneamente. Está activa.

8. Liam O'Connor es Backend Engineer con 4 años de seniority — el miembro más junior. Trabaja exclusivamente en Aegis. Está activo.

PROYECTOS (5)
-------------
1. Nebula (T01) tiene deadline el 15 de septiembre de 2026, presupuesto de $850,000 y prioridad alta. Estado: activo.

2. Horizon (T03) tiene deadline el 1 de agosto de 2026 — es el proyecto con fecha más cercana. Presupuesto de $420,000 y prioridad media. Estado: activo.

3. Aegis (T07) tiene deadline el 10 de enero de 2027, presupuesto de $1,200,000 — el mayor de todos — y prioridad crítica. Estado: activo.

4. Phoenix (T04) tiene deadline el 30 de octubre de 2026, presupuesto de $670,000 y prioridad alta. Estado: activo.

5. Atlas (T06) tiene deadline el 30 de julio de 2026 — vence en solo 13 días desde hoy. Presupuesto de $300,000 y prioridad baja. Estado: activo.

DEPENDENCIAS ENTRE PROYECTOS (7)
---------------------------------
D01: Horizon BLOQUEA a Nebula (dependencia bloqueante).
D02: Nebula depende de Aegis.
D03: Phoenix depende de Aegis.
D04: Aegis BLOQUEA a Phoenix (dependencia bloqueante).
D05: Atlas depende de Horizon (dependencia tipo legado).
D06: Nebula depende de Phoenix.
D07: Horizon BLOQUEA a Aegis (dependencia bloqueante).

Nótese que existe una dependencia circular entre Aegis y Phoenix: Aegis bloquea a Phoenix (D04), pero Phoenix depende de Aegis (D03). Además, Horizon bloquea tanto a Nebula (D01) como a Aegis (D07), creando un cuello de botella crítico.

RIESGOS IDENTIFICADOS (6)
--------------------------
R01 — CRÍTICO: Fuga de datos en el API Gateway de CloudShield. Afecta a los proyectos Horizon y Nebula. Probabilidad estimada: 35%.

R02 — ALTO: Incumplimiento del deadline de Nebula (2026-09-15). Afecta exclusivamente a Nebula. Probabilidad: 60%, la más alta de todos los riesgos.

R03 — ALTO: Rotación de Sofía Márquez (DevOps Lead). Afecta a tres proyectos simultáneamente: Aegis, Nebula y Phoenix. Probabilidad: 45%.

R04 — CRÍTICO: Vulnerabilidad zero-day en el motor de eventos de StreamCore. Afecta a Nebula y Phoenix. Probabilidad: 20%.

R05 — MEDIO: Sobrecoste del servicio DataVault (S3 Storage). Afecta exclusivamente a Aegis. Probabilidad: 55%.

R06 — ALTO: Incumplimiento de requisitos de compliance (SOC2) en Phoenix, relacionado con el proveedor ComplianceAudit. Afecta a Phoenix. Probabilidad: 40%.

DECISIONES DE ARQUITECTURA (5)
-------------------------------
AR01 (T01): Se decidió adoptar Kubernetes como plataforma de orquestación de contenedores. Aplica a Nebula, Horizon y Aegis.

AR02 (T04): Se decidió migrar la autenticación de servicios a OAuth2. Esta decisión se tomó como consecuencia directa del incidente I-004 (fuga de tokens en Aegis). Aplica a Aegis y Phoenix.

AR03 (T01): Se decidió implementar una arquitectura de motor de eventos desacoplado. Esta decisión se tomó tras el incidente I-002 (pérdida de eventos en Nebula). Aplica a Nebula y Phoenix.

AR04 (T04): Se decidió implementar rotación automática de secretos cada 72 horas. Esta decisión es consecuencia de los riesgos R01 (fuga de datos en API Gateway) y R04 (zero-day en motor de eventos). Aplica a TODOS los proyectos: Nebula, Horizon, Aegis, Phoenix y Atlas.

AR05 (T07): Se decidió implementar redundancia geográfica para DataVault. Esta decisión responde al riesgo R05 (sobrecoste). Aplica exclusivamente a Aegis.

INCIDENTES RECIENTES (4)
-------------------------
I-001 — 15 de junio de 2026: Se detectó latencia crítica en el API Gateway de Horizon, gestionado por CloudShield. Severidad alta. El incidente fue RESUELTO tras 4.5 horas de trabajo.

I-002 — 22 de junio de 2026: Se produjo pérdida de eventos en el bus de Nebula, gestionado por StreamCore. Severidad media. El incidente fue RESUELTO tras 2 horas. Como consecuencia, se tomó la decisión AR03 (motor de eventos desacoplado).

I-003 — 1 de julio de 2026: Caducó un certificado TLS en Atlas, gestionado por CloudShield. Severidad baja. RESUELTO en 1 hora.

I-004 — 10 de julio de 2026 (hace 7 días): Se detectó una fuga de tokens de acceso en Aegis, relacionado con ComplianceAudit. Severidad CRÍTICA. El incidente NO HA SIDO RESUELTO. Como consecuencia inmediata, se tomó la decisión AR02 (migración a OAuth2).

PROVEEDORES (5)
----------------
CloudShield provee WAF + API Gateway por $15,000/mes con SLA 99.99%. Da servicio a los proyectos Horizon y Nebula. Fue responsable de los incidentes I-001 e I-003.

StreamCore provee el Event Bus por $8,200/mes con SLA 99.95%. Da servicio a Nebula y Phoenix. Fue responsable del incidente I-002.

DataVault provee almacenamiento S3 por $23,000/mes — el proveedor más caro — con SLA 99.99%. Da servicio exclusivamente a Aegis. Presenta el riesgo R05 de sobrecoste.

ComplianceAudit provee servicios de compliance SOC2 por $18,000/mes con SLA 99.90%. Da servicio exclusivamente a Phoenix. Es responsable del incidente crítico I-004 (no resuelto).

NetScale provee CDN + DNS por $9,500/mes con SLA 99.99%. Da servicio a tres proyectos: Nebula, Horizon y Phoenix.
```

---

## Formato 6: XML

```xml
<?xml version="1.0" encoding="UTF-8"?>
<nexuscorp_kb>
  <equipo>
    <miembro id="Elena_Vargas">
      <rol>Arquitecta Cloud</rol>
      <proyectos>
        <proyecto>Nebula</proyecto>
        <proyecto>Horizon</proyecto>
      </proyectos>
      <seniority>12</seniority>
      <activo>true</activo>
    </miembro>
    <miembro id="Marco_Silva">
      <rol>SRE Lead</rol>
      <proyectos>
        <proyecto>Nebula</proyecto>
      </proyectos>
      <seniority>9</seniority>
      <activo>true</activo>
    </miembro>
    <miembro id="Lucía_Rojas">
      <rol>Platform Engineer</rol>
      <proyectos>
        <proyecto>Horizon</proyecto>
        <proyecto>Aegis</proyecto>
      </proyectos>
      <seniority>7</seniority>
      <activo>true</activo>
    </miembro>
    <miembro id="Daniel_Ortega">
      <rol>Security Lead</rol>
      <proyectos>
        <proyecto>Aegis</proyecto>
        <proyecto>Phoenix</proyecto>
      </proyectos>
      <seniority>11</seniority>
      <activo>true</activo>
    </miembro>
    <miembro id="Aisha_Okafor">
      <rol>Data Engineer</rol>
      <proyectos>
        <proyecto>Nebula</proyecto>
        <proyecto>Phoenix</proyecto>
      </proyectos>
      <seniority>6</seniority>
      <activo>true</activo>
    </miembro>
    <miembro id="Chen_Wei">
      <rol>Network Architect</rol>
      <proyectos>
        <proyecto>Horizon</proyecto>
      </proyectos>
      <seniority>14</seniority>
      <activo>true</activo>
    </miembro>
    <miembro id="Sofía_Márquez">
      <rol>DevOps Lead</rol>
      <proyectos>
        <proyecto>Nebula</proyecto>
        <proyecto>Aegis</proyecto>
        <proyecto>Phoenix</proyecto>
      </proyectos>
      <seniority>8</seniority>
      <activo>true</activo>
    </miembro>
    <miembro id="Liam_O'Connor">
      <rol>Backend Engineer</rol>
      <proyectos>
        <proyecto>Aegis</proyecto>
      </proyectos>
      <seniority>4</seniority>
      <activo>true</activo>
    </miembro>
  </equipo>

  <proyectos>
    <proyecto id="Nebula">
      <codigo>T01</codigo>
      <deadline>2026-09-15</deadline>
      <presupuesto>850000</presupuesto>
      <prioridad>alta</prioridad>
      <estado>activo</estado>
    </proyecto>
    <proyecto id="Horizon">
      <codigo>T03</codigo>
      <deadline>2026-08-01</deadline>
      <presupuesto>420000</presupuesto>
      <prioridad>media</prioridad>
      <estado>activo</estado>
    </proyecto>
    <proyecto id="Aegis">
      <codigo>T07</codigo>
      <deadline>2027-01-10</deadline>
      <presupuesto>1200000</presupuesto>
      <prioridad>crítica</prioridad>
      <estado>activo</estado>
    </proyecto>
    <proyecto id="Phoenix">
      <codigo>T04</codigo>
      <deadline>2026-10-30</deadline>
      <presupuesto>670000</presupuesto>
      <prioridad>alta</prioridad>
      <estado>activo</estado>
    </proyecto>
    <proyecto id="Atlas">
      <codigo>T06</codigo>
      <deadline>2026-07-30</deadline>
      <presupuesto>300000</presupuesto>
      <prioridad>baja</prioridad>
      <estado>activo</estado>
    </proyecto>
  </proyectos>

  <dependencias>
    <dependencia id="D01">
      <origen>Horizon</origen>
      <destino>Nebula</destino>
      <tipo>bloqueante</tipo>
      <descripcion>Horizon bloquea a Nebula</descripcion>
    </dependencia>
    <dependencia id="D02">
      <origen>Nebula</origen>
      <destino>Aegis</destino>
      <tipo>dependencia</tipo>
      <descripcion>Nebula depende de Aegis</descripcion>
    </dependencia>
    <dependencia id="D03">
      <origen>Phoenix</origen>
      <destino>Aegis</destino>
      <tipo>dependencia</tipo>
      <descripcion>Phoenix depende de Aegis</descripcion>
    </dependencia>
    <dependencia id="D04">
      <origen>Aegis</origen>
      <destino>Phoenix</destino>
      <tipo>bloqueante</tipo>
      <descripcion>Aegis bloquea a Phoenix</descripcion>
    </dependencia>
    <dependencia id="D05">
      <origen>Atlas</origen>
      <destino>Horizon</destino>
      <tipo>legado</tipo>
      <descripcion>Atlas depende de Horizon (legado)</descripcion>
    </dependencia>
    <dependencia id="D06">
      <origen>Nebula</origen>
      <destino>Phoenix</destino>
      <tipo>dependencia</tipo>
      <descripcion>Nebula depende de Phoenix</descripcion>
    </dependencia>
    <dependencia id="D07">
      <origen>Horizon</origen>
      <destino>Aegis</destino>
      <tipo>bloqueante</tipo>
      <descripcion>Horizon bloquea a Aegis</descripcion>
    </dependencia>
  </dependencias>

  <riesgos>
    <riesgo id="R01">
      <descripcion>Fuga de datos en API Gateway</descripcion>
      <impacto>crítico</impacto>
      <proyectos>
        <proyecto>Horizon</proyecto>
        <proyecto>Nebula</proyecto>
      </proyectos>
      <proveedor>CloudShield</proveedor>
      <probabilidad>0.35</probabilidad>
    </riesgo>
    <riesgo id="R02">
      <descripcion>Incumplimiento de deadline de Nebula</descripcion>
      <impacto>alto</impacto>
      <proyectos>
        <proyecto>Nebula</proyecto>
      </proyectos>
      <proveedor xsi:nil="true" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"/>
      <probabilidad>0.60</probabilidad>
    </riesgo>
    <riesgo id="R03">
      <descripcion>Rotación de Sofía Márquez</descripcion>
      <impacto>alto</impacto>
      <proyectos>
        <proyecto>Aegis</proyecto>
        <proyecto>Nebula</proyecto>
        <proyecto>Phoenix</proyecto>
      </proyectos>
      <proveedor xsi:nil="true" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"/>
      <probabilidad>0.45</probabilidad>
    </riesgo>
    <riesgo id="R04">
      <descripcion>Zero-day en motor de eventos</descripcion>
      <impacto>crítico</impacto>
      <proyectos>
        <proyecto>Nebula</proyecto>
        <proyecto>Phoenix</proyecto>
      </proyectos>
      <proveedor>StreamCore</proveedor>
      <probabilidad>0.20</probabilidad>
    </riesgo>
    <riesgo id="R05">
      <descripcion>Sobrecoste de DataVault</descripcion>
      <impacto>medio</impacto>
      <proyectos>
        <proyecto>Aegis</proyecto>
      </proyectos>
      <proveedor>DataVault</proveedor>
      <probabilidad>0.55</probabilidad>
    </riesgo>
    <riesgo id="R06">
      <descripcion>Incumplimiento de compliance en Phoenix</descripcion>
      <impacto>alto</impacto>
      <proyectos>
        <proyecto>Phoenix</proyecto>
      </proyectos>
      <proveedor>ComplianceAudit</proveedor>
      <probabilidad>0.40</probabilidad>
    </riesgo>
  </riesgos>

  <decisiones>
    <decision id="AR01">
      <descripcion>Adopción de Kubernetes como plataforma de orquestación</descripcion>
      <trimestre>T01</trimestre>
      <proyectos>
        <proyecto>Nebula</proyecto>
        <proyecto>Horizon</proyecto>
        <proyecto>Aegis</proyecto>
      </proyectos>
      <post_incidente xsi:nil="true" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"/>
    </decision>
    <decision id="AR02">
      <descripcion>Migración a OAuth2 para autenticación de servicios</descripcion>
      <trimestre>T04</trimestre>
      <proyectos>
        <proyecto>Aegis</proyecto>
        <proyecto>Phoenix</proyecto>
      </proyectos>
      <post_incidente>I-004</post_incidente>
    </decision>
    <decision id="AR03">
      <descripcion>Arquitectura de motor de eventos desacoplado</descripcion>
      <trimestre>T01</trimestre>
      <proyectos>
        <proyecto>Nebula</proyecto>
        <proyecto>Phoenix</proyecto>
      </proyectos>
      <post_incidente>I-002</post_incidente>
    </decision>
    <decision id="AR04">
      <descripcion>Rotación automática de secretos cada 72h</descripcion>
      <trimestre>T04</trimestre>
      <proyectos>
        <proyecto>Nebula</proyecto>
        <proyecto>Horizon</proyecto>
        <proyecto>Aegis</proyecto>
        <proyecto>Phoenix</proyecto>
        <proyecto>Atlas</proyecto>
      </proyectos>
      <post_incidente>R01,R04</post_incidente>
    </decision>
    <decision id="AR05">
      <descripcion>Redundancia geográfica de DataVault</descripcion>
      <trimestre>T07</trimestre>
      <proyectos>
        <proyecto>Aegis</proyecto>
      </proyectos>
      <post_incidente>R05</post_incidente>
    </decision>
  </decisiones>

  <incidentes>
    <incidente id="I-001">
      <descripcion>Latencia crítica en API Gateway de Horizon</descripcion>
      <fecha>2026-06-15</fecha>
      <severidad>alta</severidad>
      <proveedor>CloudShield</proveedor>
      <estado>resuelto</estado>
      <duracion_horas>4.5</duracion_horas>
    </incidente>
    <incidente id="I-002">
      <descripcion>Pérdida de eventos en el bus de Nebula</descripcion>
      <fecha>2026-06-22</fecha>
      <severidad>media</severidad>
      <proveedor>StreamCore</proveedor>
      <estado>resuelto</estado>
      <duracion_horas>2.0</duracion_horas>
    </incidente>
    <incidente id="I-003">
      <descripcion>Caducidad de certificado TLS en Atlas</descripcion>
      <fecha>2026-07-01</fecha>
      <severidad>baja</severidad>
      <proveedor>CloudShield</proveedor>
      <estado>resuelto</estado>
      <duracion_horas>1.0</duracion_horas>
    </incidente>
    <incidente id="I-004">
      <descripcion>Fuga de tokens de acceso en Aegis</descripcion>
      <fecha>2026-07-10</fecha>
      <severidad>crítica</severidad>
      <proveedor>ComplianceAudit</proveedor>
      <estado>no_resuelto</estado>
      <duracion_horas xsi:nil="true" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"/>
    </incidente>
  </incidentes>

  <proveedores>
    <proveedor id="CloudShield">
      <servicio>WAF + API Gateway</servicio>
      <costo_mensual>15000</costo_mensual>
      <proyectos>
        <proyecto>Horizon</proyecto>
        <proyecto>Nebula</proyecto>
      </proyectos>
      <sla>99.99%</sla>
    </proveedor>
    <proveedor id="StreamCore">
      <servicio>Event Bus</servicio>
      <costo_mensual>8200</costo_mensual>
      <proyectos>
        <proyecto>Nebula</proyecto>
        <proyecto>Phoenix</proyecto>
      </proyectos>
      <sla>99.95%</sla>
    </proveedor>
    <proveedor id="DataVault">
      <servicio>S3 Storage</servicio>
      <costo_mensual>23000</costo_mensual>
      <proyectos>
        <proyecto>Aegis</proyecto>
      </proyectos>
      <sla>99.99%</sla>
    </proveedor>
    <proveedor id="ComplianceAudit">
      <servicio>SOC2 Compliance</servicio>
      <costo_mensual>18000</costo_mensual>
      <proyectos>
        <proyecto>Phoenix</proyecto>
      </proyectos>
      <sla>99.90%</sla>
    </proveedor>
    <proveedor id="NetScale">
      <servicio>CDN + DNS</servicio>
      <costo_mensual>9500</costo_mensual>
      <proyectos>
        <proyecto>Nebula</proyecto>
        <proyecto>Horizon</proyecto>
        <proyecto>Phoenix</proyecto>
      </proyectos>
      <sla>99.99%</sla>
    </proveedor>
  </proveedores>
</nexuscorp_kb>
```
