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

### Entrada 7

- **Fecha:** 2026-11-22
- **Prompt o sugerencia:** Le pedí al asistente que, a partir de la regla de `registrar_compra` y de la nueva regla de `consumir_material`, propusiera particiones de equivalencia, valores límite y la tabla de decisión de la función que combina condiciones. Le exigí indicar de qué parte de la regla salía cada esperado y señalar las ambigüedades.
- **Decisión:** Aceptada con cambios
- **Por qué:** La IA propuso las particiones principales y una tabla de decisión correcta para `consumir_material`, pero al revisarla con las cinco preguntas faltaban cuatro cosas: la partición inválida del código vacío, el límite «cantidad igual a la existencia» (consumir todo), la partición de valores no finitos (`NaN`, `+∞`, `-∞`) y la ambigüedad de `historial(codigo_inexistente)`. Las agregué al registro y decidí que el filtro sin coincidencias devuelve una lista vacía.
- **Verificación:** Cada fila de las secciones 1.1 a 1.5 de `registro_pruebas.md` tiene una prueba que la cubre. Revisé que los esperados salieran de la regla y no de ejecutar el código.
- **Commit relacionado:** `docs: reescribir registro_pruebas.md con tablas formales de la semana 7`

### Entrada 8

- **Fecha:** 2026-11-22
- **Prompt o sugerencia:** «Genera pruebas de pytest a partir de la regla y de mi tabla revisada. Usa `@pytest.mark.parametrize` con un comentario por fila, `pytest.approx` para decimales, `pytest.raises` con el tipo exacto de error y esperados fijos. No modifiques el código de producción. Para cada prueba, indica de qué fila de la tabla sale el esperado.»
- **Decisión:** Aceptada con cambios
- **Por qué:** La primera versión de la IA tenía pruebas débiles: `is not None`, `pytest.raises(Exception)`, un esperado de consumo que devolvía `0` al pasarse del stock, una prueba de fecha que ignoraba la fecha explícita y una de mínimo con `<` en lugar de `<=`. Corregí o descarté ocho pruebas y conservé solo las que comprobaban la regla. Ninguna prueba se ajustó para que pasara el código.
- **Verificación:** `python -m pytest -q` reportó `58 passed`. Las pruebas corregidas fallan con las mutaciones M1 a M6, así que no son débiles.
- **Commit relacionado:** `test: suite parametrizada de compras, consumo y consultas`

### Entrada 9

- **Fecha:** 2026-11-22
- **Prompt o sugerencia:** «Genera un fixture de pytest con un catálogo ficticio de JY Velas y Jabones, con contexto local de Neiva, sin personas reales, con tildes, eñe, apóstrofo, texto vacío y valores en cero.»
- **Decisión:** Aceptada con cambios
- **Por qué:** La IA propuso nombres y códigos de materiales, pero los ajusté para incluir «Jabón de avena y ñame «Relámpago»», «Aroma d' naranja», un material con nombre vacío y un mínimo en cero. Eliminé cualquier dato que pareciera de una persona (nombres, teléfonos o documentos). El fixture quedó con alcance de función para que cada prueba reciba un inventario limpio.
- **Verificación:** `tests/conftest.py` contiene solo productos y códigos inventados. Las 58 pruebas usan el fixture sin compartir estado y no hay datos de personas reales en el repositorio.
- **Commit relacionado:** `test: datos sintéticos con casos difíciles en el fixture`

### Entrada 10

- **Fecha:** 2026-11-22
- **Prompt o sugerencia:** «Propone seis mutaciones de código para comprobar si la suite detecta errores: cambiar `<=` por `<`, `>` por `>=`, un descuento por una suma, `<=` por `<` en el mínimo, ignorar la fecha y aceptar `NaN` e infinito. Indica qué prueba debería fallar en cada caso.»
- **Decisión:** Aceptada
- **Por qué:** Las seis mutaciones son cambios pequeños y realistas, y permiten comprobar que las pruebas no solo pasan, sino que fallan cuando el código se rompe. La IA acertó en las pruebas que debían fallar; ejecuté cada mutación por separado y restauré el archivo desde una copia en memoria.
- **Verificación:** M1 falló en 4 pruebas, M2 en 1, M3 en 4, M4 en 3, M5 en 1 y M6 en 4. El SHA-256 del archivo restaurado coincide con el original. La evidencia está en `docs/mutaciones_semana7.txt` y en la sección 3 de `registro_pruebas.md`.
- **Commit relacionado:** `docs: registrar las seis mutaciones y sus resultados`

## Resumen

### Semana 5

| Decisión | Cantidad |
|---|---|
| Aceptadas | 2 |
| Aceptadas con cambios | 2 |
| Rechazadas | 2 |

### Semana 7

| Decisión | Cantidad |
|---|---|
| Aceptadas | 1 |
| Aceptadas con cambios | 3 |
| Rechazadas | 0 |

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

## Errores que atraparon las pruebas (semana 7)

- **`NaN` e infinito.** La validación original solo comprobaba `cantidad <= 0`; `NaN` no es
  mayor que cero, pero la comparación devolvía `False` y el valor se colaba. La prueba
  `test_cantidad_no_positiva_lanza_error_y_no_cambia_nada[nan]` falló con `DID NOT RAISE`;
  se agregó `math.isfinite` y la partición EP-Q4.
- **Consumir toda la existencia.** La mutación M2 cambió `>` por `>=` y la prueba
  `test_consumir_descuenta_existencia[MAT-FRASCO-10-10-0]` falló: consumir exactamente el
  stock debe ser válido.
- **Mínimo exacto.** La prueba inicial de la IA usaba `<` y no habría detectado la mutación
  M4; se corrigió a `<=` y se agregó el caso límite 5/5.
- **Fecha explícita.** La prueba de fecha de la IA esperaba `date.today()` aunque se pasara
  una fecha; se corrigió para que el esperado saliera de la regla.

## Reflexión de la semana 7

El asistente fue útil para enumerar particiones y escribir la primera versión mecánica de las
pruebas, pero la revisión fue mía: ocho pruebas de la IA eran débiles o contradecían la regla.
Lo más valioso fue ejecutar las mutaciones, porque demostraron que una prueba que pasa no sirve
si no falla cuando el código se rompe. Aprendí a separar el esperado de la regla del esperado
que sugiere el código, y a documentar las ambigüedades (historial sin coincidencias, mínimo
exacto, valores no finitos) antes de escribir la prueba. En la próxima funcionalidad empezaría
por la tabla de decisión y por los bordes, y dejaría las mutaciones como parte normal del ciclo,
no como una comprobación final.
