# Procedencia y criterio de implementación

Este paquete fue construido por traducción funcional independiente de la implementación Python suministrada por el usuario. La referencia fue tratada como autoridad de comportamiento para esta entrega.

La equivalencia se verificó mediante ejecución diferencial de entradas idénticas y comparación exacta de:

- bytes canónicos;
- HCORTEX renderizado;
- CORTEX reconstruido;
- hashes;
- diagnósticos y errores.

No se importan módulos Python en tiempo de ejecución y no existe dependencia del intérprete Python.
