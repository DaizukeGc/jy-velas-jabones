# Revisión de seguridad — jy-velas-jabones

- **Proyecto:** Sistema de control de inventario, pedidos y ventas para JY Velas y Jabones.
- **Estudiante:** Jhonier Santiago García Coqueco.
- **Repositorio:** https://github.com/DaizukeGc/jy-velas-jabones
- **Commit auditado:** `fe00949bb3d96fa88ff720956226046f4d47b22b`
- **Fecha de la revisión:** 25 de noviembre de 2026.
- **Alcance:** `jy_velas/inventario.py`, `tests/`, `pyproject.toml`,
  `requirements-dev.txt`, `.gitignore` y `.env.example`.

## 1. Herramientas y criterios

### Linter

- **Herramienta:** Ruff, configurado en `pyproject.toml`.
- **Reglas activas:** `E` (estilo PEP 8), `F` (errores lógicos), `B` (bugbear) y
  `S` (seguridad de bandit).
- **Longitud máxima de línea:** 88 caracteres.
- **Excepción justificada:** `S101` se ignora solo en `tests/*` porque `assert` es
  el mecanismo estándar de pytest.
- **Resultado:** `python -m ruff check .` → `All checks passed!`

### Dependencias

- **Herramienta:** `pip-audit`.
- **Comando:** `python -m pip_audit -r requirements-dev.txt`.
- **Resultado:** `No known vulnerabilities found`.
- **Dependencias de ejecución:** ninguna; el núcleo usa solo la biblioteca
  estándar (ADR-001).
- **Dependencia de desarrollo:** `pytest==9.2.0`, fijada en
  `requirements-dev.txt`.

### Lista de verificación aplicada

| Criterio | ¿Se cumple? | Evidencia |
|---|---|---|
| Corrección y pruebas | Sí | `python -m pytest -q` en verde; pruebas de abuso en `tests/test_seguridad_inventario.py`. |
| Diseño y legibilidad | Sí | Ruff sin avisos; funciones pequeñas con nombres del dominio. |
| Docstrings | Sí | Funciones públicas documentadas: qué hacen, qué reciben, qué devuelven y qué errores lanzan. |
| Seguridad | Sí | Validación de entradas, integridad del catálogo y dependencias auditadas. |
| Uso responsable de IA | Sí | `bitacora_ia.md` registra las decisiones, su verificación y los rechazos. |

### Revisión con IA

- **Herramienta:** OpenCode (asistente de código en el IDE, modo agente).
- **Alcance:** `jy_velas/inventario.py` y `tests/`.
- **Contraste:** cada sugerencia se verificó manualmente contra el commit
  `fe00949`; las que no se pudieron reproducir se descartaron como falsos
  positivos.

### Puntos de seguridad revisados

| Punto de seguridad | ¿Aplica? | Resultado |
|---|---|---|
| Inyección (consultas con parámetros) | No aplica a SQL/NoSQL porque el proyecto no usa bases de datos. Sí aplica a la validación de entradas de la API interna del inventario (`codigo`, `cantidad` y `fecha`). | Corregido (H-01, H-02 y H-03): validación estricta de tipo, longitud y valores finitos; se conservan los mensajes de error de negocio. |
| Secretos (código, historial, `.gitignore`, `.env.example`) | Sí aplica a la gestión del repositorio y la configuración. | Sin claves ni credenciales en el código ni en el commit `fe00949`. `.gitignore` excluye `.env`, `.env.*`, `venv/` y `.venv/`; se añadió `.env.example` como plantilla sin valores reales. |
| Contraseñas (scrypt, bcrypt o argon2 con sal) | No aplica: es una librería local de inventario sin registro, inicio de sesión ni almacenamiento de contraseñas. | Documentado como no aplicable; no se añaden mecanismos innecesarios. |
| Control de acceso (rol verificado y prueba de abuso) | No aplica control por roles ni usuarios. Sí aplica la protección contra abuso de la API interna: entradas gigantes, tipos inválidos, valores no finitos y materiales duplicados. | Corregido (H-01 a H-06): tipos, longitudes máximas, cantidades finitas, fechas válidas y catálogo sin duplicados; pruebas de abuso en `tests/test_seguridad_inventario.py`. |
| Dependencias (existen, necesarias, versión fijada, `pip-audit`) | Sí aplica: `pytest==9.2.0` fijado en `requirements-dev.txt`; no hay dependencias de ejecución. | `pip-audit` sin vulnerabilidades conocidas; `venv/` fuera del rastreo de Git mediante `.gitignore`. |

## 2. Tabla de hallazgos

| Id | Archivo y línea | Problema | Categoría OWASP | Severidad | Corrección | Commit |
|---|---|---|---|---|---|---|
| H-01 | `jy_velas/inventario.py:109-113` | `_validar_cantidad` no verifica el tipo: `bool` se acepta como `1` y un valor no numérico lanza `TypeError` en `math.isfinite`. | A03:2021 — Injection (validación de entradas) / CWE-20 | Media | Se añadió `isinstance(cantidad, (int, float))`, rechazo de `bool`, `math.isfinite` y `cantidad > 0`; se mantiene `ErrorInventario`. | `95118b9` |
| H-02 | `jy_velas/inventario.py:49-56` | `registrar_compra` no valida `fecha`; acepta cualquier objeto y lo almacena en `Compra`. | A04:2021 — Diseño inseguro / Integridad de datos | Media | Se añadió `_validar_fecha`, que exige `None` o `datetime.date`; en caso contrario lanza `ErrorInventario`. | `95118b9` |
| H-03 | `jy_velas/inventario.py:102-107` | `_buscar_material` no valida el tipo ni la longitud de `codigo`; un código no hashable lanza `TypeError` y uno gigante puede consumir memoria. | A03:2021 — Injection / A04:2021 — Diseño inseguro | Media | Se valida que `codigo` sea `str` no vacío y de máximo 50 caracteres antes de consultar el diccionario; se conserva el mensaje de material no registrado. | `95118b9` |
| H-04 | `jy_velas/inventario.py:22-30` | `Material` permite `existencia` y `minimo` negativos, `NaN` o `inf`, dejando el catálogo en estado inconsistente. | A04:2021 — Diseño inseguro / Integridad de datos | Media | Se añadió `__post_init__`, que exige números finitos no negativos y longitudes máximas para `codigo`, `nombre` y `unidad`. | `95118b9` |
| H-05 | `jy_velas/inventario.py:45-47` | `Inventario.__init__` sobrescribe silenciosamente materiales con el mismo código; se pierde existencia y mínimo. | A04:2021 — Diseño inseguro / Integridad de datos | Media | Se detectan códigos duplicados y se lanza `ErrorInventario` antes de construir el catálogo. | `95118b9` |
| H-06 | `jy_velas/inventario.py:91-100` | `materiales_bajo_minimo` devuelve referencias a los objetos `Material` internos, que son mutables; un llamador puede alterar el catálogo sin pasar por las reglas. | A01:2021 — Broken Access Control / Exposición de estado interno | Baja | Se devuelven copias con `dataclasses.replace` para que el llamador no pueda mutar el estado interno. | `95118b9` |
| H-07 | `pyproject.toml`; `requirements-dev.txt`; `inventario.py:49, 50, 54, 107` | Falta configuración de Ruff, `pytest>=8.0` no estaba fijado y cuatro líneas de `inventario.py` superaban 88 caracteres (E501). | A06:2021 — Componentes vulnerables y desactualizados / Mantenibilidad | Baja | Se añadió configuración de Ruff (E, F, B, S, línea 88, S101 ignorado en `tests`), se fijó `pytest==9.2.0` y se dividieron las líneas largas; `ruff check .` y `pip-audit` sin errores. | `95118b9` |

> Los siete hallazgos (`H-01` a `H-07`) y las 58 pruebas de abuso quedaron integrados en el commit `95118b9`.

### Avisos del linter no corregidos

| Regla | Archivo y línea | Por qué se mantiene |
|---|---|---|
| S101 | `tests/test_consultas_inventario.py`; `tests/test_consumir_material.py`; `tests/test_registrar_compra.py`; `tests/test_seguridad_inventario.py` | `assert` es la forma estándar de comprobar aserciones en pytest; se excluye en `pyproject.toml` únicamente para `tests/*`. |

### Verificación de las correcciones

| Herramienta | Comando | Resultado |
|---|---|---|
| Ruff | `python -m ruff check .` | `All checks passed!` |
| pip-audit | `python -m pip_audit -r requirements-dev.txt` | `No known vulnerabilities found` |
| pytest | `python -m pytest -q` | Suite completa en verde (compras, consumo, consultas y pruebas de abuso). |

## 3. Revisión con IA

**Prompt usado:** «Revisa el código fuente de jy-velas-jabones (módulo
`jy_velas/inventario.py` y suite `tests/`) evaluando calidad, reglas Ruff
(E, F, B, S) y criterios de seguridad (inyección, secretos, contraseñas,
control de acceso y dependencias). Entrega una tabla con archivo, línea,
severidad y justificación, separando problemas reales, falsos positivos y
sospechas comprobables.»

| Hallazgo de la IA | ¿Real o falso positivo? | Cómo lo verifiqué |
|---|---|---|
| `_validar_cantidad` no rechaza `bool` y un valor no numérico lanza `TypeError`. | Real | Revisé `jy_velas/inventario.py:109-113`: `math.isfinite(cantidad)` se ejecuta antes de comprobar el tipo; `True` es un `int` y se acepta como `1`. |
| `registrar_compra` no valida `fecha` y puede almacenar cualquier objeto en `Compra`. | Real | Comparé `registrar_compra` con `_validar_cantidad`: la cantidad se validaba, pero `fecha` se usaba directamente en `Compra(...)`. |
| `_buscar_material` no valida `codigo`; un código no hashable lanza `TypeError`. | Real | Revisé `_buscar_material`: solo captura `KeyError`; `self._materiales[[]]` lanza `TypeError` antes del `except`. |
| Uso de `math.isfinite` como posible ejecución dinámica de código. | Falso positivo | Verifiqué `inventario.py:112`: es una comprobación aritmética de números finitos, sin `eval` ni `exec`. |
| Falta de hashing seguro de contraseñas (bcrypt/argon2). | Falso positivo | Inspeccioné `inventario.py` y `tests/`: no existe autenticación, sesiones ni usuarios. |

### Lo que la IA no encontró

La revisión inicial centrada en la validación de entradas no detectó que
`Material` aceptaba valores negativos y no finitos, que `Inventario.__init__`
sobrescribía códigos duplicados ni que `materiales_bajo_minimo` exponía objetos
internos mutables. Estos hallazgos aparecieron en la inspección manual y se
registraron como H-04, H-05 y H-06. La IA tampoco señaló las cuatro líneas E501
ni la dependencia `pytest>=8.0` sin fijar, que se corrigieron como H-07. Esto
confirma que la IA es útil para enumerar sospechas, pero no reemplaza la lectura
del código ni la ejecución de las herramientas.

## 4. Pendientes

| Pendiente | Por qué no se corrigió | Plan |
|---|---|---|
| Integración continua de Ruff y `pip-audit`. | El proyecto todavía no tiene un flujo de integración continua configurado. | Añadir un flujo que ejecute `ruff check`, `pip-audit` y `pytest` en cada `push` a `main`. |
| Pruebas de carga y análisis dinámico en navegador. | El proyecto no tiene interfaz web ni base de datos; no aplica en esta iteración. | Reevaluar cuando se agregue la interfaz o la persistencia. |

**Claves expuestas:** ninguna.
