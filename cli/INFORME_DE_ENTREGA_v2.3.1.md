# Informe de Entrega — codec-cortex v2.3.1

**Versión:** 2.3.1
**Fecha:** 2026-06-30
**Licencia:** MIT
**Autor:** Fidel Ernesto Lozada A.

## Resumen

Release correctivo experimental. Tests empezaron a fallar honestamente cuando el roundtrip bidireccional CORTEX ⇄ HCORTEX no era real. v2.3.1 establece la distinción entre display-only y canónico, y prepara el terreno para el núcleo bidireccional en v2.4.0.

## Cambios principales

- Gate de reversibilidad: `reversible:true` requiere coverage 100% y cero errores.
- Distinción display vs canónico: `W_HCORTEX_DISPLAY_ONLY`.
- Documentación CORTEX/HCORTEX alineada con el estado real.
