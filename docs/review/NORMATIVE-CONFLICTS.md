# Tensiones normativas detectadas en F3-CHARTER

## NC-01 — CE-4 y glosario portable

CE-4 compara un documento que declara `micro_cur` con otro que no lo declara y pide “mismo AST”. Esto entra en tensión con I4 y con la naturaleza estructural de `$0`.

Resolución aplicada:

```text
IdeaValue(cur, micro_cur→current) == IdeaValue(current)
Document(with micro declaration) != Document(without declaration)
```

Eliminar la declaración para forzar igualdad documental sería pérdida estructural y debilitaría portabilidad.

## NC-02 — CE-7 pertenece a Fase 4

El Charter exige roundtrip HCORTEX como criterio de éxito de Fase 3, mientras el plan y Fase 2 reservan HCORTEX para Fase 4.

Resolución aplicada:

- F3 conserva toda información necesaria.
- F3 no define HCORTEX antes de su fase.
- El Gate global permanece bloqueado hasta que F4 cierre CE-7.

## NC-03 — I7 literal y strings estructurales

“Solo el focus lleva comillas” no puede aplicarse literalmente a `fields`, `desc` o textos no-focus con espacios sin romper gramática.

Resolución aplicada:

- I7 rige payload de Ideas.
- `focus:text` siempre quoted.
- `text` no-focus bare cuando es inequívoco.
- quoted permanece permitido cuando es estructuralmente necesario.
