# Plan de pruebas (Módulo 5)

## Estrategia

Pruebas primero (TDD) con `pytest`. Cada regla de negocio se expresa como particiones de
equivalencia, valores límite y una tabla de decisión antes de escribir el código. Los esperados
salem de la regla, no de ejecutar la implementación.

## Cobertura de la lógica de negocio

| Área | Archivo | Casos |
|---|---|---|
| Registro de compras (HU-01) | `tests/test_registrar_compra.py` | 21 |
| Consumo de materiales (HU-02) | `tests/test_consumir_material.py` | 20 |
| Consultas y alertas (HU-03) | `tests/test_consultas_inventario.py` | 17 |
| Abuso y seguridad (semana 6) | `tests/test_seguridad_inventario.py` | 58 |
| **Total** | | **116** |

## Casos límite cubiertos

Cantidad 1 (mínimo positivo), existencia inicial 0, consumo exacto de todo el stock, mínimo
exacto (`<=`), fecha explícita, código vacío, `NaN`, `+inf`, `-inf`, `bool`, tipos no numéricos,
longitudes excesivas, códigos duplicados y copias de objetos en alerta.

## Mutaciones

Se aplicaron seis mutaciones (M1 a M6): `<` por `<=`, `>` por `>=`, descuento por suma, mínimo
con `<`, fecha ignorada y aceptación de `NaN`/infinito. Cada mutación rompió al menos una prueba.
El detalle está en [`mutaciones_semana7.txt`](mutaciones_semana7.txt) y en
[`../registro_pruebas.md`](../registro_pruebas.md).

## Revisión de las pruebas generadas por IA

La primera versión de la IA tenía ocho pruebas débiles (`is not None`, `pytest.raises(Exception)`,
esperados que contradecían la regla). Se corrigieron o descartaron antes de aceptarlas; la
evidencia está en las entradas 8 y 10 de [`../bitacora_ia.md`](../bitacora_ia.md).

## Última ejecución

Ver [`pipeline_ultima_ejecucion.md`](pipeline_ultima_ejecucion.md).
