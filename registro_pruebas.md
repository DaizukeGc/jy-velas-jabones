# Registro de Pruebas Unitarias — HU-01 Registrar Compras de Materiales

**Proyecto:** Sistema de control de inventario, pedidos y ventas para JY Velas y Jabones  
**Estudiante:** Jhonier Santiago García Coqueco  
**Docente:** Ing. Jorge Luis Trujillo Artunduaga  
**Institución:** Fundación Escuela Tecnológica de Neiva «Jesús Oviedo Pérez»  
**Fecha:** 22 de noviembre de 2026  
**Asignatura:** Seminario de Inteligencia Artificial Aplicada al Ciclo de Vida del Software  

---

## 1. Introducción

Este documento registra el diseño formal de casos de prueba para la funcionalidad **HU-01: Registrar compras de materiales**, aplicando tres técnicas de caja negra: **particiones de equivalencia**, **análisis de valores límite** y **tablas de decisión**. El objetivo es demostrar que las pruebas cubren los requisitos del criterio de aceptación y detectan defectos en la implementación.

La funcionalidad bajo prueba es el método `Inventario.registrar_compra(codigo: str, cantidad: float, fecha: date | None = None) -> Compra`, definido en `jy_velas/inventario.py`. El contrato y los criterios de aceptación se describen en el README del repositorio.

---

## 2. Técnicas de Diseño de Casos de Prueba

### 2.1 Particiones de Equivalencia

Se identificaron las siguientes particiones para cada parámetro de entrada:

#### Parámetro `codigo` (código de material)

| Partición | Descripción | Valores representativos | Resultado esperado |
|-----------|-------------|------------------------|-------------------|
| **EP-C1** | Código registrado en el catálogo | `"MAT-CERA"`, `"MAT-FRASCO"`, `"MAT-ESENCIA"` | Compra registrada exitosamente |
| **EP-C2** | Código **no** registrado en el catálogo | `"MAT-AROMA"`, `"MAT-INEXISTENTE"`, `""` | `ErrorInventario` con mensaje "El material '...' no está registrado" |

#### Parámetro `cantidad` (cantidad comprada)

| Partición | Descripción | Valores representativos | Resultado esperado |
|-----------|-------------|------------------------|-------------------|
| **EP-Q1** | Cantidad estrictamente positiva (`cantidad > 0`) | `1`, `24`, `500`, `2000`, `0.5` | Compra registrada, existencia actualizada |
| **EP-Q2** | Cantidad cero (`cantidad == 0`) | `0` | `ErrorInventario` con mensaje "La cantidad debe ser mayor que cero" |
| **EP-Q3** | Cantidad negativa (`cantidad < 0`) | `-1`, `-500`, `-0.01` | `ErrorInventario` con mensaje "La cantidad debe ser mayor que cero" |

#### Parámetro `fecha` (fecha de compra)

| Partición | Descripción | Valores representativos | Resultado esperado |
|-----------|-------------|------------------------|-------------------|
| **EP-D1** | Fecha no proporcionada (`None`) | `None` | Se usa `date.today()` |
| **EP-D2** | Fecha explícita válida | `date(2026, 10, 24)`, `date(2026, 1, 1)` | Se guarda la fecha proporcionada |

#### Parámetro implícito: existencia inicial del material

| Partición | Descripción | Valores representativos | Resultado esperado |
|-----------|-------------|------------------------|-------------------|
| **EP-E1** | Existencia inicial positiva | `800` (Cera), `10` (Frasco) | Existencia final = inicial + cantidad |
| **EP-E2** | Existencia inicial en cero | `0` (Esencia) | Existencia final = cantidad comprada |

### 2.2 Análisis de Valores Límite

Para el parámetro numérico `cantidad`, se identifican los siguientes valores límite:

| Límite | Valor | Partición | Tipo de prueba |
|--------|-------|-----------|----------------|
| Límite inferior válido | `1` | EP-Q1 | Valor límite válido (mínimo positivo) |
| Límite inferior inválido | `0` | EP-Q2 | Valor límite inválido (cero) |
| Límite inferior inválido adyacente | `-1` | EP-Q3 | Valor límite inválido (negativo) |
| Valor típico | `24`, `500`, `2000` | EP-Q1 | Valores representativos del dominio |
| Valor fraccionario mínimo | `0.5` | EP-Q1 | Valor límite válido (positivo no entero) |

**Nota:** No se define un límite superior explícito en los requisitos; las cantidades están acotadas por la capacidad de representación de `float` en Python.

### 2.3 Tablas de Decisión

La tabla de decisión combina las condiciones de negocio para determinar el resultado esperado.

#### Tabla 1: Regla de negocio principal — Registrar compra

| Regla | Código registrado | Cantidad > 0 | Acción esperada |
|-------|-------------------|--------------|-----------------|
| R1 | Sí | Sí | Registrar compra, actualizar existencia, agregar al historial, devolver `Compra` |
| R2 | Sí | No (≤ 0) | Lanzar `ErrorInventario("La cantidad debe ser mayor que cero")`, no modificar existencia, no agregar al historial |
| R3 | No | Sí | Lanzar `ErrorInventario("El material '...' no está registrado")`, no modificar inventario |
| R4 | No | No (≤ 0) | Lanzar `ErrorInventario("El material '...' no está registrado")` (validación de código tiene prioridad) |

#### Tabla 2: Comportamiento de la fecha

| Regla | Fecha proporcionada | Fecha guardada en `Compra` |
|-------|---------------------|----------------------------|
| D1 | `None` | `date.today()` |
| D2 | `date` válida | La fecha proporcionada |

---

## 3. Casos de Prueba Derivados

A partir de las técnicas anteriores, se diseñaron **9 casos de prueba** que cubren todas las particiones, valores límite y reglas de decisión.

| ID | Nombre de la prueba | Técnica | Particiones/Valores cubiertos | Regla de decisión |
|----|---------------------|---------|-------------------------------|-------------------|
| CP-01 | `test_compra_de_cera_suma_al_inventario` | Particiones (EP-C1, EP-Q1, EP-E1) | Código válido, cantidad típica, existencia inicial > 0 | R1 |
| CP-02 | `test_compra_de_frascos_suma_al_inventario` | Particiones (EP-C1, EP-Q1, EP-E1) | Código válido, cantidad típica, existencia inicial > 0, unidad distinta | R1 |
| CP-03 | `test_compra_queda_en_el_historial_con_la_fecha_de_hoy` | Particiones (EP-C1, EP-Q1, EP-D1) | Código válido, cantidad típica, fecha `None` | R1, D1 |
| CP-04 | `test_compra_de_una_sola_unidad_es_valida` | **Valor límite** (límite inferior válido = 1) | Cantidad = 1 (mínimo positivo) | R1 |
| CP-05 | `test_compra_sobre_material_sin_existencias_es_valida` | Particiones (EP-C1, EP-Q1, EP-E2) | Código válido, cantidad típica, existencia inicial = 0 | R1 |
| CP-06 | `test_compra_con_fecha_personalizada_se_guarda_con_esa_fecha` | Particiones (EP-C1, EP-Q1, EP-D2) | Código válido, cantidad típica, fecha explícita | R1, D2 |
| CP-07 | `test_compra_con_cantidad_cero_lanza_error_y_no_cambia_existencias` | **Valor límite** (límite inferior inválido = 0) + Particiones (EP-Q2) | Cantidad = 0 | R2 |
| CP-08 | `test_compra_con_cantidad_negativa_lanza_error_y_no_cambia_existencias` | **Valor límite** (adyacente al límite = -1) + Particiones (EP-Q3) | Cantidad = -500 | R2 |
| CP-09 | `test_compra_de_material_no_registrado_lanza_error` | Particiones (EP-C2, EP-Q1) | Código no registrado, cantidad válida | R3 |

---

## 4. Cobertura de Requisitos

| Criterio de aceptación (README) | Casos de prueba que lo cubren |
|----------------------------------|-------------------------------|
| Escenario 1: compra de cera (800 g + 2000 g = 2800 g, historial con fecha de hoy) | CP-01, CP-03 |
| Escenario 2: cantidad inválida (−500 g → error, inventario en 800 g) | CP-08 |
| Cantidad = 0 → error | CP-07 |
| Material no registrado → error | CP-09 |
| Fecha personalizada | CP-06 |
| Existencia inicial en 0 | CP-05 |
| Cantidad mínima válida (1) | CP-04 |

---

## 5. Verificación de Detección de Defectos (Pruebas en Rojo)

Antes de la implementación final, se ejecutaron las pruebas contra una versión defectuosa del código para confirmar que detectan errores. El defecto documentado en la bitácora fue:

> **Defecto:** La validación de cantidad se realizaba **después** de actualizar la existencia.
> 
> **Efecto:** Al registrar una compra con cantidad negativa (−500), el método lanzaba el error correcto, pero la existencia quedaba corrupta (300 g en lugar de 800 g).
> 
> **Prueba que lo detectó:** `CP-08: test_compra_con_cantidad_negativa_lanza_error_y_no_cambia_existencias`
> 
> **Resultado:** La prueba falló con `assert 300 == 800`. Tras corregir el orden (validar primero, luego modificar), todas las pruebas pasaron.

---

## 6. Ejecución de las Pruebas

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -v
```

**Resultado esperado:** 9 pruebas superadas (9 passed).

```
tests/test_registrar_compra.py::test_compra_de_cera_suma_al_inventario PASSED
tests/test_registrar_compra.py::test_compra_de_frascos_suma_al_inventario PASSED
tests/test_registrar_compra.py::test_compra_queda_en_el_historial_con_la_fecha_de_hoy PASSED
tests/test_registrar_compra.py::test_compra_de_una_sola_unidad_es_valida PASSED
tests/test_registrar_compra.py::test_compra_sobre_material_sin_existencias_es_valida PASSED
tests/test_registrar_compra.py::test_compra_con_fecha_personalizada_se_guarda_con_esa_fecha PASSED
tests/test_registrar_compra.py::test_compra_con_cantidad_cero_lanza_error_y_no_cambia_existencias PASSED
tests/test_registrar_compra.py::test_compra_con_cantidad_negativa_lanza_error_y_no_cambia_existencias PASSED
tests/test_registrar_compra.py::test_compra_de_material_no_registrado_lanza_error PASSED
```

---

## 7. Referencias

- Myers, G. J., Badgett, T., & Thomas, T. M. (2011). *The art of software testing* (3rd ed.). John Wiley & Sons.
- IEEE Std 829-2008. (2008). *IEEE Standard for Software Test Documentation*.
- Pressman, R. S., & Maxim, B. R. (2015). *Software engineering: A practitioner's approach* (8th ed.). McGraw-Hill Education.
- Fundación Escuela Tecnológica de Neiva. (2026). *Rúbrica de calificación - Taller Semana 7: Pruebas unitarias con apoyo de IA*.

---

**Fin del documento**