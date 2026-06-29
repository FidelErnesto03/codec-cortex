# PACKAGING — Reglas de paquete limpio

## Objetivo

El tarball de release debe contener solo código fuente, artefactos canónicos y documentación. No debe incluir caches ni productos de ejecución local.

## Exclusiones obligatorias

```text
.pytest_cache/
__pycache__/
*.pyc
.coverage
.mypy_cache/
.ruff_cache/
.DS_Store
tmp/
build/
dist/
```

## Verificación

```bash
tar tzf codec_cortex-2.4.0-full.tar.gz | grep -E 'pytest_cache|__pycache__|\.pyc|\.coverage|tmp/|build/|dist/'
```

El comando debe devolver vacío.
