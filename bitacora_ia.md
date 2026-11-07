# Bitácora de uso de IA

Proyecto: Sistema de control de inventario, pedidos y ventas para JY Velas y Jabones
Estudiante: Jhonier Santiago García Coqueco
Funcionalidad: HU-01 — Registrar compras de materiales
Asistente usado: OpenCode (asistente de código en el IDE, modo agente)
Repositorio: https://github.com/DaizukeGc/jy-velas-jabones

## Entradas

### Entrada 1

- **Fecha:** 2026-11-07
- **Prompt o sugerencia:** Propuse al asistente el contrato de `registrar_compra` y le pedí una implementación con `dataclasses` y un diccionario de materiales indexado por código, sin dependencias externas.
- **Decisión:** Aceptada
- **Por qué:** El dominio es pequeño (unos 15 productos en la semana 3), la búsqueda por código queda en O(1) y se respeta el ADR-001 del README: solo biblioteca estándar en el núcleo. No hacía falta una base de datos para esta iteración.
- **Verificación:** Ejecuté `python -m pytest` y las 9 pruebas pasaron. Revisé que el diccionario `_materiales` se construya a partir del catálogo recibido en el constructor.
- **Commit relacionado:** `fc085c3` — feat: implementar registrar compra de materiales (pruebas en verde)

### Entrada 2

- **Fecha:** 2026-11-07
- **Prompt o sugerencia:** El asistente propuso que `registrar_compra` devolviera solo la nueva existencia del material (un número). Le pedí ajustarlo para que devolviera un objeto `Compra` con código, cantidad y fecha.
- **Decisión:** Aceptada con cambios
- **Por qué:** El criterio de aceptación de la HU-01 exige que la compra «aparezca en el historial con la fecha de hoy». Devolver la existencia no permitía comprobar ese requisito; el objeto `Compra` hace trazable cada movimiento y deja la existencia disponible con `existencia()`.
- **Verificación:** La prueba `test_compra_queda_en_el_historial_con_la_fecha_de_hoy` comprueba el objeto devuelto y su fecha. Pasó en verde junto con las demás.
- **Commit relacionado:** `fc085c3` — feat: implementar registrar compra de materiales (pruebas en verde)

### Entrada 3

- **Fecha:** 2026-11-07
- **Prompt o sugerencia:** El asistente sugirió guardar las compras en SQLite (o con pandas) para no perderlas al cerrar el programa.
- **Decisión:** Rechazada
- **Por qué:** Agrega complejidad y dependencias que no necesita una función de una sola operación. El ADR-001 pide solo la biblioteca estándar y la persistencia es una funcionalidad posterior. Además, la HU-01 no habla de conservar datos entre sesiones; eso corresponde a RNF-02 y se resolverá en otra iteración sin cambiar el contrato.
- **Verificación:** Las pruebas corren sin instalar nada adicional y el repositorio solo declara `pytest` como dependencia de desarrollo.
- **Commit relacionado:** `fc085c3` — feat: implementar registrar compra de materiales (pruebas en verde)

### Entrada 4

- **Fecha:** 2026-11-07
- **Prompt o sugerencia:** El asistente propuso exactamente 5 pruebas: 2 normales, 2 de límite y 1 de error, que es el mínimo de la rúbrica.
- **Decisión:** Aceptada con cambios
- **Por qué:** El mínimo no cubría dos riesgos del contrato: la compra con fecha personalizada y la compra de un material no registrado. Amplié el conjunto a 9 pruebas para cubrir los casos límite que documenté en el README (cantidad 1, existencia inicial 0, fecha explícita) y los dos errores (cantidad inválida y material inexistente).
- **Verificación:** `python -m pytest` reportó `9 passed`. Antes de la implementación, el mismo comando falló con `ModuleNotFoundError`, lo que evidencia el estado en rojo.
- **Commit relacionado:** `1c66d73` — test: pruebas de registrar compra de materiales (en rojo)

### Entrada 5

- **Fecha:** 2026-11-07
- **Prompt o sugerencia:** Con las pruebas en verde, pedí al asistente un refactor. Propuso extraer constantes para los mensajes y un método privado `_buscar_material` para quitar la búsqueda duplicada entre `registrar_compra` y `existencia`.
- **Decisión:** Aceptada
- **Por qué:** Elimina los valores mágicos («La cantidad debe ser mayor que cero» estaba repetido) y la duplicación del `get` con su validación. El comportamiento no cambia y el código queda más fácil de explicar en clase.
- **Verificación:** No modifiqué ninguna prueba. Ejecuté `python -m pytest` después del refactor y las 9 pruebas siguieron en verde.
- **Commit relacionado:** `22bd352` — refactor: constantes y busqueda de material sin duplicacion

### Entrada 6

- **Fecha:** 2026-11-07
- **Prompt o sugerencia:** El asistente propuso usar `decimal.Decimal` para las cantidades, para evitar errores de redondeo.
- **Decisión:** Rechazada
- **Por qué:** En esta funcionalidad las cantidades son magnitudes físicas (gramos, mililitros, unidades), no dinero; no hay sumas de precios ni impuestos. `Decimal` complica las comparaciones y no aporta una ventaja real aquí. Dejé `float` y usé `pytest.approx` en las pruebas.
- **Verificación:** Las pruebas de suma (800 + 2.000 = 2.800 y 10 + 24 = 34) pasan con `pytest.approx`; si más adelante se registran precios o dinero, se evaluará `Decimal` en esa funcionalidad.
- **Commit relacionado:** `fc085c3` — feat: implementar registrar compra de materiales (pruebas en verde)

## Resumen

| Decisión | Cantidad |
|---|---|
| Aceptadas | 2 |
| Aceptadas con cambios | 2 |
| Rechazadas | 2 |

## Errores que atraparon las pruebas

La primera implementación sumaba la cantidad a la existencia **antes** de validar que fuera
positiva. Con una compra de −500 g, el método lanzaba el error correcto, pero la existencia
quedaba en 300 g en vez de 800 g. La prueba
`test_compra_con_cantidad_negativa_lanza_error_y_no_cambia_existencias` falló con
`assert 300 == 800`. Corregí el orden: primero se valida la cantidad y solo después se modifica
el inventario. Volví a ejecutar `python -m pytest` y las 9 pruebas quedaron en verde. El error
no llegó al commit final, pero quedó documentado como evidencia de que las pruebas guiaron la
implementación.

## Reflexión final

El asistente me ayudó más en la parte mecánica: convertir el criterio en contrato, proponer las
clases y redactar la primera versión de las pruebas. La prueba de cantidad negativa fue la más
valiosa, porque descubrió que el orden de las validaciones importa: el error se mostraba, pero
el inventario ya estaba corrupto. Aprendí a no aceptar dependencias (SQLite, pandas, `Decimal`)
sin justificarlas contra el contrato y el ADR. En la próxima funcionalidad escribiría primero la
tabla de casos límite, revisaría que cada prueba falle por la razón correcta y solo entonces
pediría el código.
