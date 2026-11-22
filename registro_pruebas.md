# Registro de pruebas — Semana 7

**Proyecto:** Sistema de control de inventario, pedidos y ventas para JY Velas y Jabones  
**Estudiante:** Jhonier Santiago García Coqueco  
**Docente:** Ing. Jorge Luis Trujillo Artunduaga  
**Institución:** Fundación Escuela Tecnológica de Neiva «Jesús Oviedo Pérez»  
**Asignatura:** Seminario de Inteligencia Artificial Aplicada al Ciclo de Vida del Software  
**Fecha:** 22 de noviembre de 2026  
**Repositorio:** https://github.com/DaizukeGc/jy-velas-jabones

Este registro documenta el diseño formal de casos de prueba de la semana 7 con tres
técnicas de caja negra: particiones de equivalencia, análisis de valores límite y tablas
de decisión (Myers et al., 2011; Pressman & Maxim, 2015). El oráculo de cada prueba es la
regla de negocio escrita en el README y en este documento; nunca se tomó el esperado de
ejecutar el código. La suite completa tiene **58 pruebas parametrizadas** y se ejecuta con
`python -m pytest -v`.

## 0. Alcance y funciones probadas

Se probaron cinco funciones con reglas de negocio, dos de ellas con varias condiciones:

| Función | Tipo de regla | Condiciones que combina |
|---|---|---|
| `Inventario.registrar_compra` | Cálculo, validación y estado | Material registrado + cantidad finita positiva + fecha opcional |
| `Inventario.consumir_material` | Cálculo, validación y estado | Material registrado + cantidad finita positiva + cantidad ≤ existencia |
| `Inventario.existencia` | Consulta con validación | Material registrado |
| `Inventario.historial` | Consulta con filtro | Código nulo, registrado o inexistente |
| `Inventario.materiales_bajo_minimo` | Estado y valor límite | Existencia ≤ mínimo de aviso |

## 1. Reglas y tablas de casos

### 1.1 Regla: `registrar_compra` (HU-01)

**Regla completa (el oráculo).** Como dueña, quiero registrar las compras de materiales
para saber cuánto tengo de cada uno antes de hacer una tanda. Dado un material ya
registrado y una cantidad finita estrictamente mayor que cero, el sistema suma la
cantidad a la existencia, agrega la compra al historial con la fecha indicada (o con la
fecha de hoy si no se indica) y devuelve un objeto `Compra`. Si el material no está
registrado, no modifica nada y lanza `ErrorInventario` con el mensaje
«El material '<codigo>' no está registrado». Si la cantidad no es un número finito mayor
que cero, no modifica nada y lanza `ErrorInventario` con el mensaje
«La cantidad debe ser mayor que cero».

#### Particiones de equivalencia

| Parámetro | Partición | Descripción | Valores representativos |
|---|---|---|---|
| `codigo` | EP-C1 | Código registrado en el catálogo | `MAT-CERA`, `MAT-FRASCO`, `MAT-ESENCIA` |
| `codigo` | EP-C2 | Código no registrado (incluida la cadena vacía) | `MAT-AROMA`, `MAT-INEXISTENTE`, `""` |
| `cantidad` | EP-Q1 | Número finito estrictamente positivo | `0.5`, `1`, `24`, `500`, `2000` |
| `cantidad` | EP-Q2 | Cero | `0` |
| `cantidad` | EP-Q3 | Negativo finito | `-0.01`, `-1`, `-500` |
| `cantidad` | EP-Q4 | No finito | `NaN`, `+∞`, `-∞` |
| `fecha` | EP-D1 | No proporcionada | `None` |
| `fecha` | EP-D2 | Fecha explícita válida | `date(2026, 10, 24)` |
| existencia inicial | EP-E1 | Existencia inicial positiva | `800`, `10` |
| existencia inicial | EP-E2 | Existencia inicial en cero | `0` |

#### Valores límite

| Borde | Último valor de una partición | Primer valor de la siguiente | Prueba que lo cubre |
|---|---|---|---|
| Cantidad válida/inválida | `0` (EP-Q2, inválido) | `0.5` (EP-Q1, válido) | `test_cantidad_no_positiva...[0]` y `test_registrar_compra_suma...[MAT-CERA-0.5-800-800.5]` |
| Cantidad entera mínima | `0` (inválido) | `1` (válido) | `test_cantidad_no_positiva...[0]` y `test_registrar_compra_suma...[MAT-CERA-1-800-801]` |
| Cantidad negativa adyacente | `-1` (inválido) | `0` (inválido) | `test_cantidad_no_positiva...[-1]` y `...[0]` |
| Existencia inicial | `0` (EP-E2, válido) | `1` (EP-E1, válido) | `test_registrar_compra_suma...[MAT-ESENCIA-500-0-500]` |
| Fecha | `None` (EP-D1) | fecha explícita (EP-D2) | `test_fecha_por_defecto_es_hoy` y `test_fecha_personalizada_se_conserva` |

#### Tabla de decisión

| Regla | Material registrado | Cantidad finita > 0 | Resultado esperado |
|---|---|---|---|
| R1 | Sí | Sí | Suma la cantidad, agrega la compra al historial y devuelve `Compra`. |
| R2 | Sí | No | `ErrorInventario` de cantidad; no modifica existencia ni historial. |
| R3 | No | Sí | `ErrorInventario` de material; no modifica nada. |
| R4 | No | No | `ErrorInventario` de material (la validación del material ocurre primero). |

#### Tabla de casos

| Técnica | Partición o límite | Entrada | Esperado | Prueba que lo cubre |
|---|---|---|---|---|
| Partición | EP-C1, EP-Q1, EP-E1 | `MAT-CERA`, 2000, inicial 800 | Existencia 2800 | `test_registrar_compra_suma_a_la_existencia[MAT-CERA-2000-800-2800]` |
| Partición | EP-C1, EP-Q1, EP-E1, otra unidad | `MAT-FRASCO`, 24, inicial 10 | Existencia 34 | `...[MAT-FRASCO-24-10-34]` |
| Límite | Primer entero positivo válido | `MAT-CERA`, 1, inicial 800 | Existencia 801 | `...[MAT-CERA-1-800-801]` |
| Partición | EP-E2 | `MAT-ESENCIA`, 500, inicial 0 | Existencia 500 | `...[MAT-ESENCIA-500-0-500]` |
| Límite | Primer positivo fraccionario | `MAT-CERA`, 0.5, inicial 800 | Existencia 800.5 | `...[MAT-CERA-0.5-800-800.5]` |
| Límite | EP-Q2: cero | `MAT-CERA`, 0 | `ErrorInventario` de cantidad; existencia 800 y sin historial | `test_cantidad_no_positiva_lanza_error_y_no_cambia_nada[0]` |
| Límite | EP-Q3: negativo adyacente | `MAT-CERA`, -1 | `ErrorInventario` de cantidad; sin cambios | `test_cantidad_no_positiva...[-1]` |
| Partición | EP-Q3: negativos | `MAT-CERA`, -500 y -0.01 | `ErrorInventario` de cantidad; sin cambios | `test_cantidad_no_positiva...[-500]` y `[-0.01]` |
| Partición | EP-Q4: no finitos | `MAT-CERA`, `NaN`, `+∞`, `-∞` | `ErrorInventario` de cantidad; sin cambios | `test_cantidad_no_positiva...[nan]`, `[inf]`, `[-inf]` |
| Partición | EP-C2: no registrado | `MAT-AROMA`, `MAT-INEXISTENTE`, `""`, cantidad 100 | `ErrorInventario` de material; sin historial | `test_material_no_registrado_lanza_error[...]` |
| Partición | EP-D1 | fecha `None` | `date.today()` | `test_fecha_por_defecto_es_hoy` |
| Partición | EP-D2 | fecha `date(2026, 10, 24)` | La fecha explícita | `test_fecha_personalizada_se_conserva` |
| Decisión | R1 | `MAT-CERA`, 1 | Compra registrada | `test_tabla_decision_registrar_compra[MAT-CERA-1-None]` |
| Decisión | R2 | `MAT-CERA`, 0 | Error de cantidad | `...[MAT-CERA-0-La cantidad debe ser mayor que cero]` |
| Decisión | R3 | `MAT-AROMA`, 1 | Error de material | `...[MAT-AROMA-1-El material 'MAT-AROMA' no está registrado]` |
| Decisión | R4 | `MAT-AROMA`, 0 | Error de material | `...[MAT-AROMA-0-El material 'MAT-AROMA' no está registrado]` |

**Ambigüedades encontradas.** El README no decía qué hacer con `NaN` o infinito. Se
decidió rechazarlos con el mismo mensaje de cantidad inválida porque no son cantidades
físicas válidas; la decisión quedó en el ADR-003 del README. Tampoco definía si el código
vacío era «no registrado»; se trató como EP-C2 y se probó explícitamente.

### 1.2 Regla: `consumir_material` (HU-02)

**Regla completa (el oráculo).** Como dueña, quiero descontar los materiales que uso en una
tanda para saber cuánto me queda y evitar quedarme sin stock. Dado un material registrado y
una cantidad finita estrictamente mayor que cero que no supere la existencia disponible, el
sistema resta la cantidad y devuelve la existencia restante. Si el material no existe, no
modifica nada y lanza `ErrorInventario` de material. Si la cantidad no es finita y positiva,
no modifica nada y lanza `ErrorInventario` de cantidad. Si la cantidad supera la existencia,
no modifica nada y lanza `ErrorInventario` de stock insuficiente con el disponible y lo
solicitado.

#### Particiones de equivalencia

| Parámetro | Partición | Descripción | Valores representativos |
|---|---|---|---|
| `codigo` | EP-C1 | Registrado | `MAT-CERA`, `MAT-FRASCO` |
| `codigo` | EP-C2 | No registrado (incluida la cadena vacía) | `MAT-AROMA`, `MAT-INEXISTENTE`, `""` |
| `cantidad` | EP-Q1 | Finita y estrictamente positiva | `1`, `10`, `500` |
| `cantidad` | EP-Q2 | Cero | `0` |
| `cantidad` | EP-Q3 | Negativa finita | `-1`, `-0.01` |
| `cantidad` | EP-Q4 | No finita | `NaN`, `+∞`, `-∞` |
| stock | EP-S1 | Cantidad ≤ existencia | 10 de 10; 500 de 800; 1 de 800 |
| stock | EP-S2 | Cantidad > existencia | 10.01 de 10; 801 de 800; 1 de 0 |

#### Valores límite

| Borde | Último valor de una partición | Primer valor de la siguiente | Prueba que lo cubre |
|---|---|---|---|
| Cantidad válida/inválida | `0` (inválido) | `1` (válido) | `test_consumir_cantidad_no_positiva...[0]` y `test_consumir_descuenta...[MAT-CERA-1-800-799]` |
| Stock suficiente/insuficiente | `10` (válido, consume todo) | `10.01` (inválido) | `...[MAT-FRASCO-10-10-0]` y `test_consumir_mas_que_existencia...[MAT-FRASCO-10.01-10]` |
| Stock suficiente/insuficiente | `800` (válido) | `801` (inválido) | `test_consumir_descuenta...[MAT-CERA-500-800-300]` y `test_consumir_mas_que_existencia...[MAT-CERA-801-800]` |
| Existencia cero | `0` (válido para consultar) | `1` (solicitado, inválido por stock) | `test_consumir_mas_que_existencia...[MAT-ESENCIA-1-0]` |

#### Tabla de decisión completa (8 combinaciones)

| Regla | Material registrado | Cantidad finita > 0 | Cantidad ≤ existencia | Resultado |
|---|---|---|---|---|
| R1 | Sí | Sí | Sí | Descuenta y devuelve la existencia restante. |
| R2 | Sí | Sí | No | `ErrorInventario` de stock; no modifica. |
| R3 | Sí | No | Sí | `ErrorInventario` de cantidad; no modifica. |
| R4 | Sí | No | No | `ErrorInventario` de cantidad; no modifica. |
| R5 | No | Sí | Sí | `ErrorInventario` de material; no modifica. |
| R6 | No | Sí | No | `ErrorInventario` de material; no modifica. |
| R7 | No | No | Sí | `ErrorInventario` de material; no modifica. |
| R8 | No | No | No | `ErrorInventario` de material; no modifica. |

La tabla se simplifica a cinco reglas porque la validación del material tiene prioridad
sobre la cantidad, y la cantidad tiene prioridad sobre el stock: R1 (éxito), R2 (stock),
R3–R4 (cantidad) y R5–R8 (material).

#### Tabla de casos

| Técnica | Partición o límite | Entrada | Esperado | Prueba que lo cubre |
|---|---|---|---|---|
| Partición | EP-C1, EP-Q1, EP-S1 | `MAT-CERA`, 500, inicial 800 | Devuelve 300 y deja 300 | `test_consumir_descuenta_existencia[MAT-CERA-500-800-300]` |
| Límite | EP-S1: consume toda la existencia | `MAT-FRASCO`, 10, inicial 10 | Devuelve 0 y deja 0 | `...[MAT-FRASCO-10-10-0]` |
| Límite | EP-Q1 mínimo positivo | `MAT-CERA`, 1, inicial 800 | Devuelve 799 y deja 799 | `...[MAT-CERA-1-800-799]` |
| Límite | EP-S2: un gramo de más | `MAT-CERA`, 801, inicial 800 | `ErrorInventario` de stock; deja 800 | `test_consumir_mas_que_existencia_lanza_error[MAT-CERA-801-800]` |
| Límite | EP-S2: exceso fraccionario | `MAT-FRASCO`, 10.01, inicial 10 | `ErrorInventario` de stock; deja 10 | `...[MAT-FRASCO-10.01-10]` |
| Límite | EP-S2: stock cero | `MAT-ESENCIA`, 1, inicial 0 | `ErrorInventario` de stock; deja 0 | `...[MAT-ESENCIA-1-0]` |
| Límite | EP-Q2: cero | `MAT-CERA`, 0 | `ErrorInventario` de cantidad; deja 800 | `test_consumir_cantidad_no_positiva_lanza_error[0]` |
| Partición | EP-Q3: negativos | `MAT-CERA`, -1 y -0.01 | `ErrorInventario` de cantidad; deja 800 | `...[ -1]` y `[-0.01]` |
| Partición | EP-Q4: no finitos | `MAT-CERA`, `NaN`, `+∞`, `-∞` | `ErrorInventario` de cantidad; deja 800 | `...[nan]`, `[inf]`, `[-inf]` |
| Partición | EP-C2: no registrado | `MAT-AROMA`, `MAT-INEXISTENTE`, `""` | `ErrorInventario` de material | `test_consumir_material_no_registrado_lanza_error[...]` |
| Decisión | R1 | `MAT-CERA`, 1 | Éxito; deja 799 | `test_tabla_decision_consumir_material[MAT-CERA-1-ok]` |
| Decisión | R2 | `MAT-CERA`, 801 | Error de stock | `...[MAT-CERA-801-stock]` |
| Decisión | R3/R4 | `MAT-CERA`, 0 | Error de cantidad | `...[MAT-CERA-0-cantidad]` |
| Decisión | R5–R8 | `MAT-AROMA`, 1 y 0 | Error de material | `...[MAT-AROMA-1-material]` y `...[MAT-AROMA-0-material]` |

**Ambigüedades encontradas.** El README de la semana 5 no definía el consumo; se agregó
como HU-02 derivada de N-01 y se documentó su contrato en el README antes de las pruebas.
Tampoco definía si el consumo debía aparecer en `historial()`; se decidió no mezclarlo con
las compras (ADR-002) para no romper el tipo `Compra` ni las pruebas anteriores.

### 1.3 Regla: `existencia` (consulta)

**Regla completa (el oráculo).** Devuelve la existencia actual de un material registrado.
Si el código no existe en el catálogo, no devuelve un valor y lanza `ErrorInventario` con
el mensaje «El material '<codigo>' no está registrado».

| Técnica | Partición o límite | Entrada | Esperado | Prueba que lo cubre |
|---|---|---|---|---|
| Partición | EP-C1: registrado con existencia positiva | `MAT-CERA` | 800 | `test_existencia_devuelve_el_valor_del_catalogo[MAT-CERA-800]` |
| Partición | EP-C1: registrado con existencia positiva | `MAT-FRASCO` | 10 | `...[MAT-FRASCO-10]` |
| Límite | Existencia en cero | `MAT-ESENCIA` | 0 | `...[MAT-ESENCIA-0]` |
| Límite | Nombre vacío y existencia cero | `MAT-SIN-NOMBRE` | 0 | `...[MAT-SIN-NOMBRE-0]` |
| Partición | EP-C2: no registrado | `MAT-AROMA` | `ErrorInventario` de material | `test_existencia_material_no_registrado_lanza_error[MAT-AROMA]` |
| Partición | EP-C2: no registrado | `MAT-INEXISTENTE` | `ErrorInventario` de material | `...[MAT-INEXISTENTE]` |
| Límite | Cadena vacía | `""` | `ErrorInventario` de material | `...[]` |

**Ambigüedad encontrada.** Ninguna: el contrato de `existencia` ya estaba definido en la
semana 5 y se conservó sin cambios.

### 1.4 Regla: `historial` (consulta con filtro)

**Regla completa (el oráculo).** Devuelve las compras registradas en orden de inserción. Si
se indica un código, devuelve solo las compras de ese material. Si el código no existe en el
catálogo, devuelve una lista vacía porque el filtro es una consulta y no una operación de
negocio; esta decisión se documenta como ambigüedad resuelta.

| Técnica | Partición o límite | Entrada | Esperado | Prueba que lo cubre |
|---|---|---|---|---|
| Límite | Historial vacío | Sin compras | `[]` | `test_historial_vacio_al_inicio` |
| Partición | Sin filtro | Dos compras | Las dos, en orden | `test_historial_sin_filtro_devuelve_todas_en_orden` |
| Partición | Filtro con compras | `MAT-CERA` | Solo la compra de cera | `test_historial_filtra_por_codigo[MAT-CERA-esperados0]` |
| Partición | Filtro con compras | `MAT-FRASCO` | Solo la compra de frascos | `...[MAT-FRASCO-esperados1]` |
| Partición | Filtro sin compras / no registrado | `MAT-AROMA` | `[]` | `...[MAT-AROMA-esperados2]` |

**Ambigüedad encontrada.** El README no definía `historial(codigo_inexistente)`. Se decidió
devolver `[]` y no lanzar error, porque el método es una consulta de solo lectura y no
altera el inventario; la decisión quedó escrita en el docstring y en esta tabla.

### 1.5 Regla: `materiales_bajo_minimo` (alerta de estado)

**Regla completa (el oráculo).** Devuelve los materiales cuya existencia es igual o menor
que su mínimo de aviso, en el orden del catálogo. Un mínimo de cero solo genera alerta
cuando la existencia también es cero. La comparación es `<=`, no `<`: si la existencia es
exactamente el mínimo, el material ya está en el límite y debe aparecer.

| Técnica | Partición o límite | Entrada | Esperado | Prueba que lo cubre |
|---|---|---|---|---|
| Partición | Existencia por debajo del mínimo | 4.99, mínimo 5 | Incluido | `test_materiales_bajo_minimo_respeta_el_limite[4.99-5-True]` |
| Límite | Existencia igual al mínimo | 5, mínimo 5 | Incluido | `...[5-5-True]` |
| Límite | Existencia apenas por encima | 5.01, mínimo 5 | Excluido | `...[5.01-5-False]` |
| Límite | Mínimo cero y existencia cero | 0, mínimo 0 | Incluido | `...[0-0-True]` |
| Partición | Catálogo completo | Fixture sintético | Frascos, esencia, jabón y material sin nombre | `test_materiales_bajo_minimo_devuelve_todos_los_que_cumplen` |

**Ambigüedad encontrada.** El README no aclaraba si «bajo mínimo» incluía el valor exacto.
Se decidió que sí (`<=`) porque el mínimo es el umbral de aviso; si la existencia es igual
al mínimo, la dueña ya debe comprar. Esta decisión es la que detecta la mutación M4.

## 2. Pruebas de la IA descartadas o corregidas

**Prompt usado.** «Dada la regla de negocio de cada función y mi tabla de particiones y
límites, genera pruebas de pytest con `@pytest.mark.parametrize`, un comentario por fila,
`pytest.approx` para decimales, `pytest.raises` con el tipo exacto de error y esperados
fijos. No modifiques el código de producción. Para cada prueba, indica de qué fila de la
tabla sale el esperado.» La respuesta completa y la revisión están en la entrada 8 de
`bitacora_ia.md`.

| Prueba generada por la IA | Decisión | Por qué | En su lugar |
|---|---|---|---|
| `test_registrar_compra_devuelve_algo`: `assert inventario.registrar_compra("MAT-CERA", 2000) is not None` | Descartada | Es débil: pasa con cualquier objeto, incluso si no suma ni registra la fecha. No verifica la regla. | `test_registrar_compra_suma_a_la_existencia[MAT-CERA-2000-800-2800]` y `test_fecha_por_defecto_es_hoy`. |
| `test_cantidad_cero_lanza_excepcion`: `with pytest.raises(Exception)` | Corregida | El tipo era demasiado general y no comprobaba el mensaje ni que el inventario quedara intacto. | `test_cantidad_no_positiva_lanza_error_y_no_cambia_nada[0]` con `ErrorInventario`, mensaje exacto, existencia 800 e historial vacío. |
| `test_consumir_mas_que_stock_devuelve_cero`: esperaba `0.0` al consumir 801 de 800 | Corregida | El esperado salía de una suposición sobre el código, no de la regla; la regla dice error y no modificar. | `test_consumir_mas_que_existencia_lanza_error[MAT-CERA-801-800]` con `ErrorInventario` y existencia 800. |
| `test_historial_codigo_inexistente_lanza_error`: esperaba `ErrorInventario` | Descartada | La regla no define ese caso y se decidió que el filtro devuelve `[]`; la prueba contradecía la decisión documentada. | `test_historial_filtra_por_codigo[MAT-AROMA-esperados2]` con lista vacía. |
| `test_fecha_personalizada_usa_hoy`: esperaba `date.today()` aunque se pasara `date(2026, 10, 24)` | Corregida | El esperado contradecía la regla de la fecha explícita; parecía copiado de una implementación que ignoraba el parámetro. | `test_fecha_personalizada_se_conserva`, que espera `date(2026, 10, 24)`. |
| `test_compra_2000`: una sola prueba sin `parametrize` | Corregida | No cubría otra unidad, el mínimo 1, la existencia inicial 0 ni el fraccionario 0.5; era redundante con una tabla. | `test_registrar_compra_suma_a_la_existencia` con cinco filas parametrizadas. |
| `test_materiales_bajo_minimo_usa_menor_estricto`: esperaba que existencia 5 con mínimo 5 no alertara | Corregida | La regla del cliente dice «igual o menor»; el esperado de la IA usaba `<` y habría dejado pasar la mutación M4. | `test_materiales_bajo_minimo_respeta_el_limite[5-5-True]` y el caso `[0-0-True]`. |
| `test_consumir_sin_validar_no_finitos`: no incluía `NaN` ni infinito | Corregida | Faltaba la partición inválida EP-Q4; con esa omisión, `NaN` corrompía la existencia. | `test_consumir_cantidad_no_positiva_lanza_error[nan]`, `[inf]` y `[-inf]`, y las equivalentes de `registrar_compra`. |

**Resumen de la revisión.** Se conservaron las pruebas cuyo esperado salía de la regla y
se corrigieron o descartaron ocho propuestas. Ninguna prueba se ajustó para que pasara el
código: cuando el esperado no coincidía con la regla, se cambió la prueba o se corrigió el
código, y el cambio quedó anotado. La revisión aplicó las tres preguntas del taller:
¿el esperado sale de la regla?, ¿fallaría si rompo el código?, ¿cubre algo que otra prueba
no cubre?

## 3. Romper el código a propósito

Se introdujeron seis mutaciones, una a la vez, sobre `jy_velas/inventario.py`. Después de
cada cambio se ejecutó `python -m pytest -q --tb=no`; al final se restauró el archivo desde
una copia en memoria y se verificó que el SHA-256 coincidiera con el original. La evidencia
completa está en `docs/mutaciones_semana7.txt` (archivo local, no versionado).

| # | Cambio introducido | Archivo y línea | ¿Falló alguna prueba? | Pruebas que fallaron (resumen) | Qué hice |
|---|---|---|---|---|---|
| M1 | Cambiar `<=` por `<` en la validación de cantidad | `jy_velas/inventario.py:112` | Sí, 4 pruebas | `test_cantidad_no_positiva...[0]`, `test_consumir_cantidad_no_positiva...[0]` y las dos filas de decisión con cantidad 0 | Nada: la suite protege el borde 0. |
| M2 | Cambiar `>` por `>=` en la validación de stock | `jy_velas/inventario.py:80` | Sí, 1 prueba | `test_consumir_descuenta_existencia[MAT-FRASCO-10-10-0]` | Nada: el caso «consumir toda la existencia» protege el borde. |
| M3 | Cambiar el descuento por una suma | `jy_velas/inventario.py:88` | Sí, 4 pruebas | Las tres filas de `test_consumir_descuenta_existencia` y la fila `ok` de la tabla de decisión | Nada: el cálculo está cubierto. |
| M4 | Cambiar `<=` por `<` en la alerta de mínimo | `jy_velas/inventario.py:99` | Sí, 3 pruebas | `test_materiales_bajo_minimo_devuelve_todos_los_que_cumplen`, `...[5-5-True]` y `...[0-0-True]` | Nada: el borde «igual al mínimo» ya estaba agregado tras la revisión de la IA. |
| M5 | Ignorar la fecha personalizada | `jy_velas/inventario.py:54` | Sí, 1 prueba | `test_fecha_personalizada_se_conserva` | Nada: la prueba de fecha explícita cubre el parámetro. |
| M6 | Quitar `math.isfinite` y aceptar `NaN` e infinito | `jy_velas/inventario.py:112` | Sí, 4 pruebas | `test_cantidad_no_positiva...[nan]` y `[inf]`, y las equivalentes de `consumir_material` | Nada: la partición EP-Q4 ya estaba cubierta. |

**Conclusión de las mutaciones.** Las seis mutaciones fueron detectadas por al menos una
prueba; no fue necesario agregar casos después de ejecutarlas. La única omisión que se
corrigió durante la revisión fue la del mínimo con `<` (M4): la prueba inicial de la IA no
habría fallado con ese cambio, así que se corrigió el esperado a `<=` y se agregó el caso
límite 5/5 antes de ejecutar las mutaciones.

## 4. Datos de prueba

**Origen.** Los datos son sintéticos y fueron generados con apoyo de IA a partir del
contexto local de JY Velas y Jabones (Neiva). No se usaron datos de personas reales, ni
nombres, teléfonos o documentos de clientes. Los materiales son ficticios y los precios no
intervienen en esta funcionalidad.

**Fixture.** `tests/conftest.py` define `catalogo_sintetico` con alcance de función: cada
prueba recibe un inventario nuevo para que no haya estado compartido entre casos.

**Casos difíciles incluidos.**

- Tildes y eñe: «Jabón de avena y ñame «Relámpago»».
- Apóstrofo: «Aroma d' naranja».
- Comillas angulares: «Relámpago».
- Texto vacío: material `MAT-SIN-NOMBRE` con nombre `""` y código vacío `""` en las pruebas
  de error.
- Valores en cero: existencia 0 en `MAT-ESENCIA` y `MAT-SIN-NOMBRE`; mínimo 0 en
  `MAT-SIN-NOMBRE`.
- Valores no finitos: `NaN`, `+∞` y `-∞` en las pruebas de cantidad inválida.
- Fraccionarios: 0.5 en la compra y 10.01 en el consumo.

**Confirmación.** No hay datos de personas reales en el repositorio ni en la suite. El
fixture solo contiene nombres de productos y códigos inventados.

## 5. Ejecución y cobertura de la rúbrica

**Comando de ejecución.**

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -v
```

**Resultado.** `58 passed` en 0.12 s. La suite se ejecutó también después de cada mutación
para comprobar que las pruebas fallan cuando el código tiene un error.

| Criterio de la rúbrica | Evidencia en este registro |
|---|---|
| 1. Tabla de casos (20) | Secciones 1.1 a 1.5: reglas, particiones válidas e inválidas, límites y tablas de decisión para las dos funciones con varias condiciones. |
| 2. Suite de pruebas (20) | 58 pruebas en tres archivos, con `parametrize`, `pytest.approx`, `pytest.raises(ErrorInventario)` y esperados exactos; todas pasan. |
| 3. Revisión de las pruebas de la IA (15) | Sección 2: ocho pruebas corregidas o descartadas, con razón y reemplazo; ninguna se ajustó al código. |
| 4. Romper el código (10) | Sección 3: seis mutaciones, archivo y línea, pruebas que fallaron y restauración verificada. |
| 5. Datos de prueba (10) | Sección 4: fixture sintético con contexto local, tildes, eñe, apóstrofo, texto vacío y ceros; sin datos reales. |
| 6. Registro de pruebas (15) | Este documento, con decisiones, razones, ambigüedades y reemplazos. |
| 7. Uso responsable y bitácora (10) | Entradas 7 a 10 de `bitacora_ia.md`, con prompt, resultado y verificación. |

**Trazabilidad de los commits de la semana 7.** Los cambios se separaron en commits
pequeños: uno para el código y el contrato, uno para la suite parametrizada, uno para este
registro y uno para la bitácora. El historial completo se consulta con `git log --oneline`.

## 6. Referencias

Fundación Escuela Tecnológica de Neiva. (2026). *Rúbrica de calificación del taller de la
semana 7: suite de pruebas del proyecto con IA y registro de pruebas* [Documento de la
asignatura]. Fundación Escuela Tecnológica de Neiva «Jesús Oviedo Pérez».

García Coqueco, J. S. (2026). *Documento de requisitos del proyecto final* [Documento de la
semana 3]. Fundación Escuela Tecnológica de Neiva «Jesús Oviedo Pérez».

IEEE. (2008). *IEEE standard for software test documentation* (IEEE Std 829-2008). Institute
of Electrical and Electronics Engineers.

Myers, G. J., Badgett, T., & Thomas, T. M. (2011). *The art of software testing* (3rd ed.).
John Wiley & Sons.

OpenCode. (2026). *OpenCode* [Asistente de código para el IDE]. https://opencode.ai

Pressman, R. S., & Maxim, B. R. (2015). *Software engineering: A practitioner's approach*
(8th ed.). McGraw-Hill Education.

pytest. (2026). *pytest documentation*. https://docs.pytest.org/

Python Software Foundation. (2026). *Python 3.11 documentation*. https://docs.python.org/3.11/
