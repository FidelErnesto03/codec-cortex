# codec-cortex-node

Implementación **Node.js sin dependencias externas** funcionalmente equivalente a la referencia Python suministrada para:

- CORTEX 0.1: modelo AST, escalares y parser.
- C14N-0.1: canonicalización determinista e idempotente.
- HCORTEX-0.1: render canónico y compilación inversa mediante esquemas pareados.
- Gates F3/F4: arnés de corpus, hashes, roundtrip y reportes de conformidad.

La implementación conserva los nombres públicos originales en `snake_case` y también ofrece alias idiomáticos en `camelCase`.

## Requisitos

- Node.js 18 o superior.
- No requiere `npm install` para ejecutar la CLI o importar el paquete.

## Instalación local

```bash
npm install ./codec-cortex-node
```

También puede ejecutarse directamente:

```bash
node ./bin/codec-cortex-node.js --help
```

## CLI

```bash
codec-cortex-node parse archivo.cortex
codec-cortex-node canonicalize archivo.cortex -o canonical.cortex
codec-cortex-node to-hcortex archivo.cortex -o archivo.md
codec-cortex-node from-hcortex archivo.md -o reconstruido.cortex
codec-cortex-node hash archivo.cortex
codec-cortex-node test RUTA_C14N RUTA_HCORTEX --report rev-report-node.json
```

`-` puede usarse como entrada para leer desde `stdin`.

La invocación compatible con la CLI Python original también está disponible:

```bash
codec-cortex-node RUTA_C14N RUTA_HCORTEX
```

## API

```js
const {
  parseCortex,
  canonicalize,
  renderHcortex,
  compileHcortex,
  c14nHash,
} = require('codec-cortex-node');

const document = parseCortex(source);
const canonical = canonicalize(document);
const hcortex = renderHcortex(document);
const [restored, diagnostics] = compileHcortex(hcortex);
const roundtrip = canonicalize(restored);
const hash = c14nHash(Buffer.from(canonical, 'utf8'));
```

Nombres equivalentes de la referencia:

```js
const {
  parse_cortex,
  render_hcortex,
  compile_hcortex,
  run_phase3,
  run_phase4,
  run_all_tests,
} = require('codec-cortex-node');
```

## Módulos

```text
src/scalars.js   Scalar, ParseError, cursor, strings, listas y attrs
src/parser.js    AST y parser CORTEX 0.1
src/c14n.js      C14N-0.1
src/hcortex.js   renderer y compiler HCORTEX-0.1
src/harness.js   gates F3/F4 y reporte
src/index.js     API pública agregada
bin/             CLI
examples/        caso integral y salidas golden verificadas
```

## Compatibilidad observada

La validación incluida compara resultados de referencia en:

- orden canónico por bytes UTF-8 y NFC;
- declaraciones format, enum, micro, namespace, extension y meta;
- símbolos globales y namespaced;
- shapes `attrs`, `attrs-pos`, `relacion`, `cuerpo` y `bloque`;
- string, atom, integer, decimal, boolean, null y list;
- expansión de microtokens;
- render y compilación HCORTEX;
- diagnósticos y códigos de error;
- hash con dominio `CORTEX-C14N-0.1`.

## Pruebas

```bash
npm test
npm run lint
```

Los archivos `examples/full.*` son vectores golden producidos con la implementación Python original y verificados byte a byte desde Node.js.

## Consideraciones de fidelidad

`canonicalize()` conserva el comportamiento de la referencia y **muta el AST recibido**. Si se requiere preservar el documento original, debe volver a parsearse la fuente o clonarse el árbol antes de canonicalizar.

La implementación reproduce el alcance de la referencia entregada; no agrega runtime de agentes, learning, perfiles obligatorios, VIEW ni gobierno de proyectos.
