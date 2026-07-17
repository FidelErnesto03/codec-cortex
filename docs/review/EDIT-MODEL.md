# Modelo de edición controlada de HCORTEX-CANONICAL

**Document ID:** `HCORTEX-EDIT-MODEL-001`

## 1. Objetivo

Permitir edición humana real sin que el archivo deje de ser auditable o dependa de una reconstrucción probabilística.

## 2. Ciclo correcto

```text
abrir HCORTEX-CANONICAL
        ↓
editar contenido visible
        ↓
compile estricto
        ↓
validar contratos y referencias
        ↓
render canónico
        ↓
mostrar diff
        ↓
aceptar nueva versión CORTEX
```

No se recomienda escribir directamente sobre el CORTEX canónico cuando la finalidad es revisión humana extensa; tampoco se recomienda reemplazar el canon por el Markdown antes de recompilar.

## 3. Clases de edición

### 3.1 Valor

Ejemplos:

- cambiar `status`;
- editar `content`;
- modificar una celda posicional;
- alterar texto o bloque.

Validación: tipo, required/optional, enum y limits.

### 3.2 Estructura local

Ejemplos:

- agregar una Idea;
- eliminar una Idea;
- reordenar Ideas;
- cambiar la sección de una Idea.

Validación: metadata, heading, unicidad y referencias.

### 3.3 Glosario

Ejemplos:

- agregar sigilo;
- modificar contrato;
- cambiar shape;
- agregar enum o microtoken.

Debe ejecutarse como operación reforzada porque puede reinterpretar múltiples Ideas simultáneamente.

### 3.4 Identidad

Cambiar `namespace`, `symbol`, `name` o `section` cambia la dirección local. El editor debe mostrar referencias afectadas y exigir actualización explícita.

## 4. Detección de conflicto

| Conflicto | Resultado |
|---|---|
| heading cambiado, metadata intacta | `H432` |
| metadata cambiada, heading intacto | `H432` |
| campo renombrado sin contrato | `H442` |
| shape cambiado solo en metadata | `H432/H484` |
| Idea movida sin actualizar metadata | `H432` |
| referencia queda huérfana | `H471` |
| READABLE presentado como CANONICAL | `H402/H485` |

## 5. Reparación asistida

Un editor puede proponer:

- sincronizar metadata con heading;
- actualizar referencias después de rename;
- ordenar campos según contrato;
- completar un fence;
- convertir layout tolerado a layout canónico.

Pero la propuesta debe ser un patch visible. Ninguna reparación puede inventar contenido semántico o convertir una ambigüedad en hecho certificado.

## 6. Regla de canon

```text
HCORTEX editado ≠ canon
HCORTEX editado + compile + validate + canonical write = nuevo canon
```
