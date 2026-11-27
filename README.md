# JY Velas y Jabones — Núcleo de inventario, pedidos y ventas

**Proyecto final del Seminario de Inteligencia Artificial Aplicada al Ciclo de Vida del Software**
Fundación Escuela Tecnológica de Neiva «Jesús Oviedo Pérez»
Autor: Jhonier Santiago García Coqueco
Docente: Ing. Jorge Luis Trujillo Artunduaga
Fecha: 7 de noviembre de 2026 (actualizado el 25 de noviembre de 2026)

## Qué es

Este repositorio contiene la primera funcionalidad del proyecto final (semana 5): el registro
de compras de materiales del sistema de JY Velas y Jabones. La funcionalidad se construyó con
pruebas primero (TDD), un asistente de código en el IDE y una bitácora de las decisiones tomadas.
En la semana 6 se hizo una auditoría de calidad y seguridad del código
([`revision_seguridad.md`](revision_seguridad.md)) y en la semana 7 se agregaron el consumo de
materiales y las alertas de mínimo, con una suite de 116 pruebas parametrizadas y un registro
formal de casos.

## Funcionalidad de la semana 5

### Historia de usuario

**HU-01 (prioridad Must, origen N-01).**
Como dueña, quiero registrar las compras de materiales para saber cuánto tengo de cada uno
antes de hacer una tanda.

**Criterio de aceptación**

- **Escenario 1 (normal): compra de cera.** Dado que hay 800 g de «Cera de soja», cuando
  registro la compra de 2.000 g, entonces el inventario queda en 2.800 g y la compra aparece
  en el historial con la fecha de hoy.
- **Escenario 2 (error): cantidad inválida.** Dado que hay 800 g de «Cera de soja», cuando
  intento registrar una compra de −500 g, entonces el sistema no la guarda, muestra
  «La cantidad debe ser mayor que cero» y el inventario sigue en 800 g.

### Contrato de la función

#### Firma

```python
from datetime import date

class Inventario:
    def registrar_compra(
        self,
        codigo: str,
        cantidad: float,
        fecha: date | None = None,
    ) -> Compra: ...
```

#### Qué recibe

| Parámetro | Tipo | Descripción |
|---|---|---|
| `codigo` | `str` | Código del material ya registrado en el catálogo (por ejemplo, `"MAT-CERA"`). |
| `cantidad` | `float` | Cantidad comprada, mayor que cero, expresada en la unidad del material (g, ml o unidad). |
| `fecha` | `date \| None` | Fecha de la compra. Si es `None`, se usa `date.today()`. |

#### Qué devuelve

Devuelve un objeto inmutable `Compra` con tres datos: `codigo_material`, `cantidad` y `fecha`.
Además, actualiza la existencia del material y agrega la compra al historial.

#### Supuestos

1. El material debe existir antes de registrar la compra (el catálogo se crea en otra operación).
2. La cantidad se expresa en la misma unidad del material; no se hacen conversiones.
3. El sistema es de un solo usuario, funciona sin internet y en esta iteración guarda los datos en memoria.
4. No se manejan compras simultáneas ni concurrencia.
5. Las cantidades son números; el dinero no interviene en esta funcionalidad.

#### Casos límite y errores

- `cantidad == 0`: se rechaza con `ErrorInventario("La cantidad debe ser mayor que cero")`.
- `cantidad < 0`: se rechaza con el mismo mensaje y no se modifica el inventario.
- `cantidad == 1`: es válida (el menor valor positivo aceptado).
- Existencia inicial en `0`: es válida; la existencia queda igual a la cantidad comprada.
- Código no registrado: se rechaza con `ErrorInventario("El material '<codigo>' no está registrado")`.
- Fecha no indicada: se registra con `date.today()`.

#### Ejemplos de entrada y salida

| # | Operación | Existencia inicial | Resultado |
|---|---|---|---|
| 1 | `registrar_compra("MAT-CERA", 2000)` | 800 g | Existencia 2.800 g; la compra queda en el historial con la fecha de hoy. |
| 2 | `registrar_compra("MAT-FRASCO", 24)` | 10 unidades | Existencia 34 unidades. |
| 3 | `registrar_compra("MAT-ESENCIA", 500)` | 0 ml | Existencia 500 ml. |
| 4 | `registrar_compra("MAT-CERA", 0)` | 800 g | `ErrorInventario("La cantidad debe ser mayor que cero")`; sigue en 800 g y no queda registro. |
| 5 | `registrar_compra("MAT-AROMA", 100)` | No existe | `ErrorInventario("El material 'MAT-AROMA' no está registrado")`. |

## Funcionalidad de la semana 7: consumo de materiales y alertas de mínimo

Esta iteración agrega dos reglas de negocio al mismo módulo de inventario. La primera
descuenta los materiales que se consumen al iniciar una tanda; la segunda lista los
materiales que llegaron a su mínimo de aviso. No se modificó la funcionalidad de la
semana 5: las compras siguen registrándose igual y el historial de compras se conserva.

### Regla de negocio (oráculo)

**HU-02 (derivada de N-01).** Como dueña, quiero descontar los materiales que uso en una
tanda para saber cuánto me queda y evitar quedarme sin stock.

- El material debe existir en el catálogo.
- La cantidad consumida debe ser un número finito estrictamente mayor que cero.
- No se puede consumir más de la existencia disponible; si se intenta, no se modifica el
  inventario y se informa cuánto hay disponible.
- Un material está «bajo mínimo» cuando su existencia es igual o menor que su mínimo de
  aviso. Un mínimo de cero solo genera alerta cuando la existencia también es cero.

**HU-03 (derivada de N-01).** Como dueña, quiero ver qué materiales están en su mínimo
para comprarlos antes de la próxima tanda.

### Contratos

```python
class Inventario:
    def consumir_material(self, codigo: str, cantidad: float) -> float: ...
    def materiales_bajo_minimo(self) -> list[Material]: ...
```

| Método | Recibe | Devuelve | Errores |
|---|---|---|---|
| `consumir_material` | `codigo` del catálogo y `cantidad` finita > 0 | Existencia restante (`float`) | `ErrorInventario` si el material no existe, la cantidad no es positiva o supera la existencia. |
| `materiales_bajo_minimo` | Nada | Lista de `Material` con `existencia <= minimo`, en el orden del catálogo | Ninguno. |

### Tabla de decisión de `consumir_material`

| Regla | Material registrado | Cantidad finita > 0 | Cantidad <= existencia | Resultado |
|---|---|---|---|---|
| R1 | Sí | Sí | Sí | Descuenta y devuelve la existencia restante. |
| R2 | Sí | Sí | No | `ErrorInventario` de stock insuficiente; no modifica. |
| R3 | Sí | No | No importa | `ErrorInventario` de cantidad inválida; no modifica. |
| R4 | No | No importa | No importa | `ErrorInventario` de material no registrado. |

Las reglas R3 y R4 se simplifican: la validación del material ocurre antes que la de la
cantidad y la del stock. La tabla completa con las ocho combinaciones está en
[`registro_pruebas.md`](registro_pruebas.md).

## Requisitos

- Python 3.11 o superior.
- `pip` para instalar la dependencia de desarrollo.
- No hay dependencias de ejecución: el núcleo usa solo la biblioteca estándar
  (ADR-001).
- Git (opcional, para clonar el repositorio).

## Instalación

```bash
git clone https://github.com/DaizukeGc/jy-velas-jabones.git
cd jy-velas-jabones
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

## Ejecución

La librería se usa desde Python; no tiene interfaz gráfica ni servidor web en
esta iteración. Ejemplo mínimo:

```python
from jy_velas.inventario import Inventario, Material

inventario = Inventario([Material("MAT-CERA", "Cera de soja", "g", 800, 500)])
inventario.registrar_compra("MAT-CERA", 2000)
print(inventario.existencia("MAT-CERA"))  # 2800
```

## Pruebas

```bash
python -m pytest -v
```

Resultado esperado: **116 pruebas superadas**.

## Pruebas incluidas

La carpeta `tests/` contiene **116 pruebas parametrizadas**:

- `tests/conftest.py`: fixture `catalogo_sintetico` con datos ficticios de JY Velas y
  Jabones (tildes, eñe, apóstrofo, comillas angulares, nombre vacío y valores en cero).
- `tests/test_registrar_compra.py`: 21 casos de la HU-01 (particiones, límites, errores y
  tabla de decisión).
- `tests/test_consumir_material.py`: 20 casos de la HU-02 (consumo, stock insuficiente,
  cantidades no positivas y tabla de decisión).
- `tests/test_consultas_inventario.py`: 17 casos de `existencia`, `historial` y
  `materiales_bajo_minimo`.
- `tests/test_seguridad_inventario.py`: 58 casos de abuso (tipos inválidos, valores no
  finitos o negativos, longitudes excesivas, fechas inválidas y códigos duplicados).

El detalle de cada caso, la revisión de las pruebas generadas por IA y las mutaciones
está en [`registro_pruebas.md`](registro_pruebas.md).

## Estructura del repositorio

```text
.
├── jy_velas/
│   ├── __init__.py
│   └── inventario.py          # HU-01, HU-02 y HU-03
├── tests/
│   ├── conftest.py            # datos sintéticos compartidos
│   ├── test_registrar_compra.py
│   ├── test_consumir_material.py
│   ├── test_consultas_inventario.py
│   └── test_seguridad_inventario.py
├── registro_pruebas.md        # diseño de casos, revisión de IA y mutaciones
├── revision_seguridad.md      # auditoría de calidad y seguridad (semana 6)
├── bitacora_ia.md             # bitácora de uso del asistente
├── README.md
├── pyproject.toml
├── requirements-dev.txt
├── .env.example               # plantilla de variables de entorno
└── .gitignore
```

## Decisiones de diseño

- **ADR-001. Solo biblioteca estándar en el núcleo del dominio.** La lógica de inventario usa
  `dataclasses`, `datetime` y tipos nativos de Python. No se agregan dependencias de ejecución;
  `pytest` es solo una dependencia de desarrollo. Así el núcleo puede reutilizarse después en la
  interfaz web o móvil sin arrastrar librerías pesadas.
- **Datos en memoria para esta iteración.** La persistencia (archivo local o base de datos) se
  difiere a una funcionalidad posterior; el contrato de `Inventario` no cambia cuando se agregue.
- **Fechas como `datetime.date`.** Se evita el texto libre para que el historial sea comparable y
  verificable.
- **Errores de negocio con `ErrorInventario`.** La interfaz podrá mostrar el mensaje al usuario sin
  exponer excepciones técnicas.
- **ADR-002. El consumo no se mezcla con el historial de compras.** `historial()` sigue
  devolviendo solo compras. Mezclar entradas y salidas en una misma lista obligaría a cambiar el
  tipo `Compra` y a romper las pruebas de la semana 5; el consumo se resolverá con un historial
  de movimientos en una iteración posterior.
- **ADR-003. Solo cantidades finitas.** Se rechazan `NaN` e infinito con el mismo mensaje de
  cantidad inválida porque no son cantidades físicas válidas, aunque el README original solo
  hablaba de «mayor que cero».

## Registro de pruebas

El diseño formal de casos (particiones de equivalencia, valores límite, tablas de decisión),
la revisión de las pruebas generadas por IA y las mutaciones aplicadas al código están en
[`registro_pruebas.md`](registro_pruebas.md).

## Bitácora de uso de IA

La bitácora completa está en [`bitacora_ia.md`](bitacora_ia.md). Registra las sugerencias del
asistente aceptadas, ajustadas y rechazadas, con su verificación y el commit relacionado. Las
entradas 11 a 14 documentan la auditoría de seguridad de la semana 6; las entradas 7 a 10, el
diseño de casos, la generación de pruebas, los datos sintéticos y las mutaciones de la semana 7.

## Autor

Jhonier Santiago García Coqueco — Fundación Escuela Tecnológica de Neiva «Jesús Oviedo Pérez».

## Licencia

Proyecto académico del Seminario de Inteligencia Artificial Aplicada al Ciclo de Vida del
Software. El código se publica con fines educativos y no se ofrece garantía de ningún tipo.
