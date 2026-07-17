# Seguridad

## Alcance

El parser opera sobre entradas no confiables y no ejecuta contenido CORTEX/HCORTEX. No resuelve rutas, URLs, extensiones ni código incluido en bloques.

## Riesgos pendientes

- límites de tamaño y profundidad aún no configurables;
- regex y documentos enormes requieren benchmark de consumo;
- listas anidadas pueden consumir memoria proporcional a la entrada;
- no existe fuzz report adjunto todavía;
- los diagnósticos pueden incluir fragmentos de entrada.

## Requisitos antes de release pública

1. `cargo fuzz` sobre parser, escalares y compiler HCORTEX;
2. límites explícitos para bytes, líneas, nesting, secciones e ideas;
3. SBOM y auditoría de dependencias;
4. `Cargo.lock` versionado;
5. revisión de licencias;
6. pruebas de denial of service;
7. verificación de artefactos instalados.

## Reporte

No se ha definido todavía un canal público de seguridad. No publique el crate hasta establecerlo.
