# JY Velas y Jabones — Núcleo de inventario, pedidos y ventas

**Proyecto final del Seminario de Inteligencia Artificial Aplicada al Ciclo de Vida del Software**
Fundación Escuela Tecnológica de Neiva «Jesús Oviedo Pérez»
Autor: Jhonier Santiago García Coqueco
Docente: Ing. Jorge Luis Trujillo Artunduaga
Fecha: 7 de noviembre de 2026

Este repositorio contiene la primera funcionalidad del proyecto final (semana 5): el registro
de compras de materiales del sistema de JY Velas y Jabones. La funcionalidad se construyó con
pruebas primero (TDD), un asistente de código en el IDE y una bitácora de las decisiones tomadas.

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

### Cómo ejecutar las pruebas

```bash
python -m pip install -r requirements-dev.txt
python -m pytest
```

Resultado esperado: **9 pruebas superadas**.

### Pruebas incluidas

El archivo `tests/test_registrar_compra.py` contiene **9 pruebas**:

**Casos normales**
- `test_compra_de_cera_suma_al_inventario`
- `test_compra_de_frascos_suma_al_inventario`
- `test_compra_queda_en_el_historial_con_la_fecha_de_hoy`

**Casos límite**
- `test_compra_de_una_sola_unidad_es_valida`
- `test_compra_sobre_material_sin_existencias_es_valida`
- `test_compra_con_fecha_personalizada_se_guarda_con_esa_fecha`

**Casos de error**
- `test_compra_con_cantidad_cero_lanza_error_y_no_cambia_existencias`
- `test_compra_con_cantidad_negativa_lanza_error_y_no_cambia_existencias`
- `test_compra_de_material_no_registrado_lanza_error`

## Estructura del repositorio

```text
.
├── jy_velas/
│   ├── __init__.py
│   └── inventario.py          # HU-01: registrar compras de materiales
├── tests/
│   └── test_registrar_compra.py
├── docs/
│   ├── generar_informe.py     # genera el informe APA 7
│   ├── Informe_Semana_5.docx
│   └── Informe_Semana_5.pdf
├── bitacora_ia.md             # bitácora de uso del asistente
├── README.md
├── pyproject.toml
├── requirements-dev.txt
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

## Bitácora de uso de IA

La bitácora completa está en [`bitacora_ia.md`](bitacora_ia.md). Registra las sugerencias del
asistente aceptadas, ajustadas y rechazadas, con su verificación y el commit relacionado.

## Autor

Jhonier Santiago García Coqueco — Fundación Escuela Tecnológica de Neiva «Jesús Oviedo Pérez».
