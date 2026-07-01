---
view: display-only
reversible: false
profile: HCORTEX-HOWTO
source: skill/cortex/SKILL.md §3, docs/cortex/api/
mode: READABLE
---

# Guías How-to HCORTEX

> **source:** skill/cortex/SKILL.md §3:HDL:* · docs/cortex/api/*

Procedimientos prácticos para tareas comunes con CODEC-CORTEX.

---

## 1. Cómo crear un archivo `.cortex`

| Paso | Acción | source |
|:----:|--------|--------|
| 1 | `cortex new miarchivo.cortex` | `docs/cortex/api/canonicalize.cortex` |
| 2 | Editar el archivo generado | `$0:canonical_sigils` |
| 3 | `cortex verify --strict miarchivo.cortex` | `docs/cortex/api/verify.cortex` |

**Secciones requeridas:**

| Sección | Contenido | Obligatorio | source |
|:-------:|-----------|:-----------:|--------|
| `$0` | Glosario | ✅ Siempre | `$0:canonical_sigils` |
| `$1` | Identidad | ✅ Siempre | `$1:IDN:project` |
| `$2`+ | Estado operativo | Según propósito | `$3:HDL:*` |

---

## 2. Cómo verificar

| Acción | Comando | source |
|--------|---------|--------|
| Verificación básica | `cortex verify --strict archivo.cortex` | `docs/cortex/api/verify.cortex` |
| Cobertura VIEW | `cortex verify-view archivo.cortex` | `docs/cortex/api/verify.cortex` |
| Roundtrip | `cortex roundtrip archivo.cortex` | `docs/cortex/api/convert.cortex` |
| Roundtrip bidireccional | `cortex roundtrip-bidir archivo.cortex` | `docs/cortex/api/convert.cortex` |
| Firma (E2) | `cortex verify --signature archivo.cortex` | `docs/cortex/api/verify.cortex` |
| Scan secretos (E2) | `cortex doctor --scan-secrets archivo.cortex` | `docs/cortex/api/doctor.cortex` |

---

## 3. Cómo agregar VIEW directives

| Campo | Valores | source |
|-------|---------|--------|
| `kind` | `table`, `kv_table`, `prose`, `puml`, `numbered_list`, `callout` | `$13:VIEW:*` |
| `target` | `$N:SIGIL:name`, `$N:SIGIL:*`, `$N:NAME` | `$13:VIEW:*` |
| `reverse` | `rows_to_entries`, `row_to_attrs`, `body_to_cuerpo`, etc. | `$13:VIEW:*` |

```cortex
$13
VIEW:mi_vista{kind:"table",target:"$3:FCS:*",reverse:"rows_to_entries",status:cur,title:"Mis Entradas de Foco"}
```

```bash
cortex verify-view archivo.cortex
```

---

## 4. Cómo ejecutar benchmarks

| Acción | Comando | source |
|--------|---------|--------|
| Listar | `cortex benchmark --list` | `docs/cortex/api/benchmark.cortex` |
| Inspeccionar | `cortex benchmark --inspect v2.0.0` | `docs/cortex/api/benchmark.cortex` |
| JSON | `cortex benchmark --list --format json` | `docs/cortex/api/benchmark.cortex` |

---

## 5. Cómo usar `cortex docstring`

| Objetivo | Comando | source |
|:--------:|---------|--------|
| Un comando | `cortex docstring canonicalize` | `docs/cortex/api/docstring.cortex` |
| Todos | `cortex docstring --all` | `docs/cortex/api/docstring.cortex` |
| Root personalizado | `cortex docstring canonicalize --docs-root docs/cortex/api` | `docs/cortex/api/docstring.cortex` |
| JSON | `cortex docstring canonicalize --format json` | `docs/cortex/api/docstring.cortex` |

---

## 6. Cómo recuperar archivos legacy

| Acción | Comando | source |
|--------|---------|--------|
| Recuperación básica | `cortex recover legacy.cortex --out recuperado.cortex` | `!hcortex_expand` |
| Con trazabilidad | `cortex recover legacy.cortex --out recuperado.cortex --embed-aud-rsk` | `!:extend_glossary` |

---

## 7. Cómo auditar y escanear secretos

| Acción | Comando | source |
|--------|---------|--------|
| Iniciar auditoría | `cortex audit on` | `docs/cortex/api/audit.cortex` |
| Estado | `cortex audit status` | `docs/cortex/api/audit.cortex` |
| Instantánea | `cortex audit snapshot` | `docs/cortex/api/audit.cortex` |
| Scan secretos | `cortex doctor --scan-secrets brain.cortex` | `docs/cortex/api/doctor.cortex` |
| Diagnóstico completo | `cortex doctor --strict` | `docs/cortex/api/doctor.cortex` |

---

## 8. Cómo cerrar una sesión

| Paso | Acción | source |
|:----:|--------|--------|
| 1 | `cortex add brain.cortex --section 5 --sigil SES --name sesion_001 --attrs '...'` | `$3:HDL:session_close` |
| 2 | `cortex add brain.cortex --section 5 --sigil LNG --name patron --attrs '...'` | `$3:HDL:session_close` |
| 3 | `cortex add brain.cortex --section 6 --sigil NXT --name seg --attrs '...'` | `$3:HDL:session_close` |
| 4 | `cortex verify --strict brain.cortex` | `docs/cortex/api/verify.cortex` |
| 5 | `cortex doctor --scan-secrets brain.cortex` | `docs/cortex/api/doctor.cortex` |
| 6 | `git add brain.cortex && git commit -m "sesión: resumen"` | `!:precommit_verify` |

---

## Ver también

| Tema | source |
|------|--------|
| Tutorial completo | `docs/es/hcortex/tutorials/primeros-pasos.md` |
| Explicación del protocolo | `docs/es/hcortex/explanations/protocolo-documentacion.md` |
| Referencia rápida | `docs/es/hcortex/reference/README.md` |
