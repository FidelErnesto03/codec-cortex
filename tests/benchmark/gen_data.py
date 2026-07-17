#!/usr/bin/env python3
"""Generate benchmark data in 6 formats from a single source of truth."""
import json, yaml_available

# === SOURCE OF TRUTH ===
DATA = {
    "team": [
        {"id": "T01","nombre":"Elena Vargas","rol":"Arquitecta Cloud","proyectos":["Nebula","Horizon"],"seniority":12,"contacto":"elena@nexuscorp.io"},
        {"id": "T02","nombre":"Marco Silva","rol":"SRE Lead","proyectos":["Nebula"],"seniority":9,"contacto":"marco@nexuscorp.io"},
        {"id": "T03","nombre":"Lucía Rojas","rol":"Platform Engineer","proyectos":["Horizon","Aegis"],"seniority":7,"contacto":"lucia@nexuscorp.io"},
        {"id": "T04","nombre":"Daniel Ortega","rol":"Security Lead","proyectos":["Aegis","Phoenix"],"seniority":11,"contacto":"daniel@nexuscorp.io"},
        {"id": "T05","nombre":"Aisha Okafor","rol":"Data Engineer","proyectos":["Nebula","Phoenix"],"seniority":6,"contacto":"aisha@nexuscorp.io"},
        {"id": "T06","nombre":"Chen Wei","rol":"Network Architect","proyectos":["Horizon"],"seniority":14,"contacto":"chen@nexuscorp.io"},
        {"id": "T07","nombre":"Sofia Márquez","rol":"DevOps Lead","proyectos":["Nebula","Aegis","Phoenix"],"seniority":8,"contacto":"sofia@nexuscorp.io"},
        {"id": "T08","nombre":"Liam O'Connor","rol":"Backend Engineer","proyectos":["Aegis"],"seniority":4,"contacto":"liam@nexuscorp.io"},
    ],
    "projects": [
        {"id":"P01","nombre":"Nebula","deadline":"2026-09-15","estado":"en ejecución","responsable":"T01","presupuesto":850000,"criticidad":"alta"},
        {"id":"P02","nombre":"Horizon","deadline":"2026-08-01","estado":"en revisión","responsable":"T03","presupuesto":420000,"criticidad":"media"},
        {"id":"P03","nombre":"Aegis","deadline":"2027-01-10","estado":"planificado","responsable":"T07","presupuesto":1200000,"criticidad":"crítica"},
        {"id":"P04","nombre":"Phoenix","deadline":"2026-10-30","estado":"en ejecución","responsable":"T04","presupuesto":670000,"criticidad":"alta"},
        {"id":"P05","nombre":"Atlas","deadline":"2026-07-30","estado":"completado","responsable":"T06","presupuesto":300000,"criticidad":"baja"},
    ],
    "dependencies": [
        {"id":"D01","origen":"Horizon","destino":"Nebula","tipo":"bloqueante","nota":"Nebula no puede avanzar sin el API Gateway de Horizon"},
        {"id":"D02","origen":"Nebula","destino":"Aegis","tipo":"dependencia","nota":"Aegis consume servicios de Nebula"},
        {"id":"D03","origen":"Phoenix","destino":"Aegis","tipo":"dependencia","nota":"Phoenix migra datos desde Aegis"},
        {"id":"D04","origen":"Aegis","destino":"Phoenix","tipo":"bloqueante","nota":"Phoenix requiere el schema de Aegis para arrancar"},
        {"id":"D05","origen":"Atlas","destino":"Horizon","tipo":"legado","nota":"Horizon hereda infraestructura de Atlas"},
        {"id":"D06","origen":"Nebula","destino":"Phoenix","tipo":"dependencia","nota":"Phoenix usa el motor de eventos de Nebula"},
        {"id":"D07","origen":"Horizon","destino":"Aegis","tipo":"bloqueante","nota":"Aegis necesita los certificados TLS gestionados por Horizon"},
    ],
    "risks": [
        {"id":"R01","desc":"Fuga de datos por API Gateway no asegurado","impacto":"crítico","proyectos":["Horizon","Nebula"],"proveedor":"CloudShield","probabilidad":0.35,"mitigacion":"WAF + rate limiting antes del launch"},
        {"id":"R02","desc":"Deadline de Nebula comprometido por dependencia Horizon","impacto":"alto","proyectos":["Nebula"],"proveedor":"N/A","probabilidad":0.60,"mitigacion":"Paralelizar tareas no bloqueantes"},
        {"id":"R03","desc":"Rotación de personal en Aegis (Sofia es clave en 3 proyectos)","impacto":"alto","proyectos":["Aegis","Nebula","Phoenix"],"proveedor":"N/A","probabilidad":0.25,"mitigacion":"Plan de sucesión y documentación"},
        {"id":"R04","desc":"Vulnerabilidad zero-day en el motor de eventos","impacto":"crítico","proyectos":["Nebula","Phoenix"],"proveedor":"StreamCore","probabilidad":0.15,"mitigacion":"Sandboxing y auditoría de dependencias"},
        {"id":"R05","desc":"Sobrecoste de proveedor DataVault por ampliación de Aegis","impacto":"medio","proyectos":["Aegis"],"proveedor":"DataVault","probabilidad":0.50,"mitigacion":"Lock de precio a 12 meses"},
        {"id":"R06","desc":"Incumplimiento de compliance SOC2 en Phoenix","impacto":"alto","proyectos":["Phoenix"],"proveedor":"ComplianceAudit","probabilidad":0.20,"mitigacion":"Pre-auditoría en septiembre"},
    ],
    "decisions": [
        {"id":"AR01","titulo":"Adoptar Kubernetes como plataforma unificada","fecha":"2026-03-12","tomada_por":"T01","afecta":["Nebula","Horizon","Aegis"],"consecuencia_de":"N/A"},
        {"id":"AR02","titulo":"Migrar autenticación a OAuth2/OIDC centralizado","fecha":"2026-04-28","tomada_por":"T04","afecta":["Aegis","Phoenix"],"consecuencia_de":"I-004"},
        {"id":"AR03","titulo":"Desacoplar el motor de eventos en un servicio independiente","fecha":"2026-05-15","tomada_por":"T01","afecta":["Nebula","Phoenix"],"consecuencia_de":"I-002"},
        {"id":"AR04","titulo":"Establecer rotación de secretos cada 72h","fecha":"2026-06-01","tomada_por":"T04","afecta":["Nebula","Horizon","Aegis","Phoenix"],"consecuencia_de":"R01,R04"},
        {"id":"AR05","titulo":"Contratar redundancy provider para DataVault","fecha":"2026-06-20","tomada_por":"T07","afecta":["Aegis"],"consecuencia_de":"R05"},
    ],
    "incidents": [
        {"id":"I-001","fecha":"2026-06-15","severidad":"alta","proyecto":"Horizon","desc":"Latencia de 400ms en API Gateway bajo carga","proveedor":"CloudShield","resuelto":True,"causa":"Rate limiting mal configurado"},
        {"id":"I-002","fecha":"2026-06-22","severidad":"media","proyecto":"Nebula","desc":"Pérdida de eventos por saturación del bus","proveedor":"StreamCore","resuelto":True,"causa":"Buffer insuficiente en consumidor"},
        {"id":"I-003","fecha":"2026-07-01","severidad":"baja","proyecto":"Atlas","desc":"Certificate expiration en monitoring","proveedor":"CloudShield","resuelto":True,"causa":"Auto-renewal no configurado"},
        {"id":"I-004","fecha":"2026-07-10","severidad":"crítica","proyecto":"Aegis","desc":"Exposición de tokens OAuth en logs públicos","proveedor":"ComplianceAudit","resuelto":False,"causa":"Debug mode activo en producción"},
    ],
    "providers": [
        {"id":"V01","nombre":"CloudShield","servicio":"WAF + API Gateway","contrato":"anual","costo_mensual":15000,"contacto":"support@cloudshield.io","riesgos":["R01"],"proyectos":["Horizon","Nebula"]},
        {"id":"V02","nombre":"StreamCore","servicio":"Event Bus + Message Queue","contrato":"mensual","costo_mensual":8200,"contacto":"ops@streamcore.io","riesgos":["R04"],"proyectos":["Nebula","Phoenix"]},
        {"id":"V03","nombre":"DataVault","servicio":"Almacenamiento cifrado S3-compatible","contrato":"anual","costo_mensual":23000,"contacto":"sales@datavault.com","riesgos":["R05"],"proyectos":["Aegis"]},
        {"id":"V04","nombre":"ComplianceAudit","servicio":"Auditoría SOC2 + ISO27001","contrato":"por proyecto","costo_mensual":18000,"contacto":"audit@complianceaudit.org","riesgos":["R06"],"proyectos":["Phoenix"]},
        {"id":"V05","nombre":"NetScale","servicio":"CDN + DNS Global","contrato":"anual","costo_mensual":9500,"contacto":"noc@netscale.net","riesgos":[],"proyectos":["Nebula","Horizon","Phoenix"]},
    ],
}

# === Generate 6 formats ===
OUT = "/home/vatrox/workspace/CODEC-CORTEX/tests/benchmark/benchmark-data.md"
lines = []

# --- FORMAT 1: CORTEX ---
lines.append("### §C — CORTEX 0.1")
lines.append("```cortex")
lines.append("$0")
lines.append("$0:format{cortex:0.1,encoding:UTF-8,language:es,type:knowledge}")
lines.append("TEA:member{type:attrs,weight:H,fields:\"id:text|nombre:text|rol:text|proyectos:text|seniority:number|contacto:text\",focus:nombre,schema:table,desc:\"Miembro del equipo\"}")
lines.append("PRJ:project{type:attrs,weight:H,fields:\"id:text|nombre:text|deadline:text|estado:text|responsable:text|presupuesto:number|criticidad:text\",focus:nombre,schema:table,desc:\"Proyecto\"}")
lines.append("DEP:dependency{type:attrs,weight:H,fields:\"id:text|origen:text|destino:text|tipo:%tipo|nota:text\",focus:nota,schema:table,desc:\"Dependencia\"}")
lines.append("RSK:risk{type:attrs,weight:H,fields:\"id:text|desc:text|impacto:%impacto|proyectos:text|proveedor:text|probabilidad:number\",focus:desc,schema:table,desc:\"Riesgo\"}")
lines.append("DEC:decision{type:attrs,weight:H,fields:\"id:text|titulo:text|fecha:text|tomada_por:text|afecta:text\",focus:titulo,schema:table,desc:\"Decisión de arquitectura\"}")
lines.append("INC:incident{type:attrs,weight:H,fields:\"id:text|fecha:text|severidad:text|proyecto:text|desc:text|proveedor:text|resuelto:%bool\",focus:desc,schema:table,desc:\"Incidente\"}")
lines.append("PRV:provider{type:attrs,weight:H,fields:\"id:text|nombre:text|servicio:text|contrato:text|costo_mensual:number|contacto:text\",focus:nombre,schema:table,desc:\"Proveedor\"}")

for cat, items in [
    ("$1: EQUIPO", DATA["team"]),
    ("$2: PROYECTOS", DATA["projects"]),
    ("$3: DEPENDENCIAS", DATA["dependencies"]),
    ("$4: RIESGOS", DATA["risks"]),
    ("$5: DECISIONES", DATA["decisions"]),
    ("$6: INCIDENTES", DATA["incidents"]),
    ("$7: PROVEEDORES", DATA["providers"]),
]:
    lines.append(cat)
    for item in items:
        vals = ",".join(f'{k}:{json.dumps(v) if isinstance(v,str) else str(v)}' for k,v in item.items())
        sigil = {"team":"TEA","projects":"PRJ","dependencies":"DEP","risks":"RSK","decisions":"DEC","incidents":"INC","providers":"PRV"}
        lines.append(f'{sigil[cat.split(": ")[0].replace("$1: ","").replace("$2: ","").replace("$3: ","").replace("$4: ","").replace("$5: ","").replace("$6: ","").replace("$7: ","").lower()]}:item{{{vals}}}')
lines.append("```")
lines.append("")

# Quick and dirty: let me just generate this properly
print("Data generation placeholder")
