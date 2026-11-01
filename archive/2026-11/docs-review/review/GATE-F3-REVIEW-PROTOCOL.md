# Protocolo independiente de Gate F3 — Charter Review

**Document ID:** `CORTEX-GATE-F3-CHARTER-002`  
**Status:** `gate-blocked / protocol-ready`

## Autoridad

1. `CORTEX-F3-CHARTER-001`
2. `CORTEX-SPEC-0.1-DRAFT-REAL-001`
3. `CORTEX-CANONICALIZATION-0.1-DRAFT-CHARTER-REVIEW-002`
4. corpus y vectores de esta entrega

## Ejecución requerida

Para los 40 casos:

```text
parse(input)
canonicalize(input) == golden bytes
canonicalize(golden) == golden
canonical hash == vector
losses == []
```

Para los 32 pares:

```text
canonicalize(left) == canonicalize(right)
```

debe coincidir con el resultado esperado.

## Requisitos adicionales del Charter

- Implementación Python independiente.
- Implementación Rust independiente escrita desde la especificación.
- Ninguna puede inspeccionar los oracles antes de congelar su primera versión.
- Comparación binaria de los 40 outputs y hashes.
- Locale y orden de filesystem perturbados.
- Cierre de HCORTEX-CANONICAL roundtrip en Fase 4.
- Revisión de tercero.

## Casos de control obligatorios

- E026: reordenar `$0` después de `format` no cambia hash.
- E027: `0.750` y `0.75` son distintos.
- E030: NFC/NFD dentro de `bloque` son distintos.
- E031: microtoken posicional expandido coincide.
- E032: quoted/bare no-focus text coincide por contrato.

## Veredicto

```text
F3 PASSED = Python independent PASS
          + Rust independent PASS
          + 40/40 byte identity
          + 32/32 equivalence
          + HCORTEX CE-7 PASS in F4
          + zero BLOCKER/HIGH ambiguity
          + external review
```

La evidencia interna y Node auxiliar no pueden emitir `F3 PASSED`.
