# Plan de operación (Módulo 6)

## Monitoreo

La watch principal es `materiales_bajo_minimo()`: devuelve los materiales con
`existencia <= minimo`. La dueña debe consultarla antes de cada tanda. No hay métricas de
servidor porque la librería se ejecuta localmente.

## Alertas

| Situación | Señal | Acción |
|---|---|---|
| Existencia igual o menor al mínimo | `materiales_bajo_minimo()` lista el material | Reponer con `registrar_compra` |
| Cantidad inválida | `ErrorInventario("La cantidad debe ser mayor que cero")` | Corregir el dato y reintentar |
| Material no registrado | `ErrorInventario("El material '...' no está registrado")` | Verificar el catálogo |
| Stock insuficiente | `ErrorInventario` con disponible y solicitado | Ajustar la cantidad o reponer |

## Respaldo y continuidad

Los datos viven en memoria: al cerrar el proceso se pierden. La persistencia está planificada
como RNF-09 / N-09 y no se implementó en este incremento. Mientras tanto, el historial se
conserva en el objeto `Inventario` durante la sesión.

## Seguridad operativa

- `.env` y `.env.*` excluidos por `.gitignore`; plantilla vacía en `.env.example`.
- Sin credenciales, contraseñas ni datos personales reales.
- `ruff`, `pip-audit` y `pytest` se ejecutan antes de cada entrega.

## Evidencia

- [`../revision_seguridad.md`](../revision_seguridad.md).
- [`pipeline_ultima_ejecucion.md`](pipeline_ultima_ejecucion.md).
