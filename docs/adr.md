# Registros de decisiones arquitectónicas (ADR)

## ADR-001 — Solo biblioteca estándar en el núcleo

- **Contexto:** la microempresa no tiene servidor y el núcleo debe ejecutarse en cualquier
  Python 3.11 sin instalación de paquetes.
- **Decisión:** `jy_velas/inventario.py` usa `dataclasses`, `datetime`, `math` y `typing`.
  `pytest` es solo dependencia de desarrollo.
- **Consecuencias:** la lógica es portable y auditables; persistencia e interfaz se agregan
  fuera del núcleo. Se rechazaron SQLite, pandas y `python-dotenv`.

## ADR-002 — El consumo no se mezcla con el historial de compras

- **Contexto:** las compras son entradas y los consumos son salidas con semántica distinta.
- **Decisión:** `historial()` devuelve solo objetos `Compra`; el consumo no agrega entradas.
- **Consecuencias:** se conserva el contrato de la semana 5 y las pruebas existentes. El
  historial de movimientos se resolverá en otra iteración.

## ADR-003 — Solo cantidades finitas y positivas

- **Contexto:** `NaN` e infinito pasaban la comprobación `> 0` y podían corromper el stock.
- **Decisión:** toda cantidad se valida con `isinstance(..., (int, float))`, rechazo de `bool`,
  `math.isfinite` y `> 0`.
- **Consecuencias:** errores de negocio predecibles (`ErrorInventario`) y mensajes estables.

## Evidencia

- [`../jy_velas/inventario.py`](../jy_velas/inventario.py), funciones `_validar_cantidad` y
  `consumir_material`.
- [`../bitacora_ia.md`](../bitacora_ia.md), entradas 3, 6 y 12.
