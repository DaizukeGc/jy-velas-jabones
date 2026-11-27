# Informe final del proyecto integrador

Proyecto: JY Velas y Jabones — núcleo de inventario, pedidos y ventas
Estudiante: Jhonier Santiago García Coqueco
Repositorio: https://github.com/DaizukeGc/jy-velas-jabones
Fecha: 2026-11-26

## 1. Resumen

La dueña de una microempresa de velas y jabones artesanales en Neiva no podía saber con certeza cuánto material tenía antes de preparar una tanda: llevaba el control en hojas de cálculo y apuntes en papel. Construí una librería de Python (Python Software Foundation, 2026) que registra compras, descuenta consumos y lista los materiales en su mínimo, con contrato explícito y sin dependencias de ejecución. Usé inteligencia artificial (IA) en las seis fases del ciclo de vida: para acotar el problema y la herramienta, extraer requisitos de una entrevista simulada, proponer diagramas y decisiones arquitectónicas, generar el código con desarrollo guiado por pruebas (TDD), crear particiones y casos de prueba, y revisar seguridad y dependencias. La verificación fue continua: pruebas en rojo y verde, ocho pruebas débiles corregidas, seis mutaciones que rompieron la suite, linter (Ruff, 2026) y auditoría de dependencias (Python Packaging Authority, 2026). Estado final: 116 pruebas superadas, Ruff sin avisos, pip-audit sin vulnerabilidades y siete hallazgos de seguridad corregidos. El resultado principal no fue que la IA escribiera código, sino que cada salida fue contrastada con una regla, una prueba o una herramienta antes de aceptarla.

**Palabras clave:** inteligencia artificial, ciclo de vida del software, pruebas, seguridad, inventario.

## 2. Problema y usuario

El usuario es la dueña-operadora de JY Velas y Jabones, una microempresa artesanal ubicada en Neiva. Antes de este proyecto registraba las entradas de cera, frascos y esencias en una hoja de cálculo y apuntaba los consumos diarios en papel. Cuando llegaba el momento de producir una tanda, no tenía una forma confiable de saber si había stock suficiente ni qué materiales debía reponer, y las alertas de agotamiento aparecían tarde. El problema no era estético sino operativo: necesitaba tres operaciones simples y confiables para controlar su materia prima: registrar una compra con fecha, descontar lo consumido en una tanda sin pasarse del stock disponible y consultar qué materiales están en o por debajo de su mínimo de aviso.

La propuesta inicial del módulo 1 está documentada en [docs/propuesta.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/propuesta.md) y el levantamiento de requisitos del módulo 2 en [docs/requisitos.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/requisitos.md). La entrevista de levantamiento, compuesta por nueve preguntas sobre inventario, compras, consumos, alertas, pedidos, ventas, reportes, acceso multiusuario y persistencia, fue simulada por un compañero en el rol de la dueña y declarada explícitamente así en el repositorio: no se utilizaron datos de personas reales. A partir de esa sesión se relevaron 11 necesidades (`N-01` a `N-11`) y 10 historias de usuario, de las cuales las tres historias de prioridad *Must* del incremento son `HU-01`, `HU-02` y `HU-03` (50 % del conjunto *Must/Should*), todas terminadas y verificadas:

| Historia | Necesidad | Operación y criterio de aceptación principal | Estado | Evidencia |
|---|---|---|---|---|
| `HU-01` | `N-01`, `N-02` | Registrar compra con código, cantidad finita > 0 y fecha opcional; suma a la existencia y devuelve objeto inmutable `Compra`. | Terminada | [README.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/README.md), [test_registrar_compra.py](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/tests/test_registrar_compra.py) |
| `HU-02` | `N-01`, `N-03` | Descontar consumo de una tanda; falla con `ErrorInventario` si no hay stock suficiente y nunca deja el inventario negativo ni alterado. | Terminada | [requisitos.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/requisitos.md), [test_consumir_material.py](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/tests/test_consumir_material.py) |
| `HU-03` | `N-04` | Listar materiales con `existencia <= minimo` en el orden del catálogo, devolviendo copias seguras para evitar mutación externa. | Terminada | [inventario.py](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/jy_velas/inventario.py), [test_consultas_inventario.py](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/tests/test_consultas_inventario.py) |

El alcance se limitó de forma intencional a la capa de dominio y a su verificación automatizada: no se construyó interfaz gráfica, base de datos ni autenticación, porque ninguna de esas piezas aparecía en los criterios de aceptación del incremento. Esa decisión quedó registrada en [docs/adr.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/adr.md) (`ADR-001`) y permitió mantener un núcleo simple, portable y explicable sin intermediarios técnicos. La solución se instala y verifica localmente con comandos simples de Python, como detalla la [guía de despliegue](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/despliegue.md).

## 3. La IA en el ciclo de vida

Utilicé OpenCode en modo agente dentro del IDE como asistente transversal en las seis fases del ciclo de vida del software, aplicando siempre la misma regla: la IA propone, y el criterio humano contrastado con el contrato, las pruebas o las herramientas automáticas decide qué se acepta, qué se ajusta y qué se rechaza.

| Módulo y fase | Qué hice con IA | Herramienta | Evidencia (enlace) | Cómo verificaste |
|---|---|---|---|---|
| 1. Fundamentos | Convertir el problema operativo en una propuesta acotada y definir el alcance del dominio | OpenCode | [docs/propuesta.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/propuesta.md) | Comprobé que el usuario, el problema y los criterios de éxito fueran verificables; fijé `ADR-001` de solo biblioteca estándar |
| 2. Requisitos | Extraer necesidades (`N-01` a `N-11`), historias de usuario, requisitos no funcionales (`RNF-01` a `RNF-05`) y criterios Gherkin | OpenCode | [docs/requisitos.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/requisitos.md), [bitacora_ia.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/bitacora_ia.md) | Revisé cada esperado contra la regla de negocio y documenté la ambigüedad de `historial()` sin coincidencias |
| 3. Diseño | Proponer diagramas de contexto C4, secuencia de compra, modelo de nueve entidades y registros ADR | OpenCode + Mermaid CLI | [docs/diseno.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/diseno.md), [docs/adr.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/adr.md) | Contrasté los diagramas con el contrato de 13 operaciones y verifiqué coherencia de las nueve entidades y los tres ADR con el código |
| 4. Código | Implementar `Inventario`, `Material` y `Compra` siguiendo ciclo TDD (rojo-verde-refactor) | OpenCode | [jy_velas/inventario.py](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/jy_velas/inventario.py), [commit fc085c3](https://github.com/DaizukeGc/jy-velas-jabones/commit/fc085c3), [commit 22bd352](https://github.com/DaizukeGc/jy-velas-jabones/commit/22bd352) | Pruebas en rojo primero (`1c66d73`), verde después (`fc085c3`), refactor sin alterar pruebas (`22bd352`); corregí el orden de validación |
| 5. Pruebas | Generar particiones de equivalencia, valores límite, tablas de decisión, fixture sintético y suite parametrizada | OpenCode | [registro_pruebas.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/registro_pruebas.md), [tests/](https://github.com/DaizukeGc/jy-velas-jabones/tree/main/tests) | Descarté o reescribí ocho pruebas débiles, ejecuté seis mutaciones (`M1` a `M6`) y validé 58 pruebas funcionales + 58 de abuso |
| 6. Operación | Auditar seguridad con lista de verificación OWASP, configurar linter, fijar dependencias y documentar despliegue | OpenCode + Ruff (2026) + pip-audit (Python Packaging Authority, 2026) | [revision_seguridad.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/revision_seguridad.md), [pipeline_ultima_ejecucion.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/pipeline_ultima_ejecucion.md) | Descarté dos falsos positivos de la IA (`math.isfinite` y hashing), añadí cuatro hallazgos manuales (`H-04` a `H-07`) y dejé el pipeline en verde |

Cada interacción relevante quedó registrada en [bitacora_ia.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/bitacora_ia.md) con fecha, prompt o sugerencia, decisión, justificación, verificación y commit asociado. En total se documentaron **14 entradas**: **3 aceptadas** sin cambios, **7 aceptadas con cambios** y **4 rechazadas** por violar el alcance, introducir dependencias innecesarias o debilitar el contrato de errores.

## 4. Verificación: lo que la IA hizo mal y cómo lo encontraste

La verificación sistemática reveló fallos concretos de la IA en cuatro fases distintas del ciclo de vida. En ninguno de los casos se modificó la regla de negocio para acomodar la salida del asistente.

### Caso 1: El histórico de un código inexistente

- **Fase:** requisitos.
- **Qué propuso la IA:** que `historial(codigo_inexistente)` lanzara `ErrorInventario`, igual que una compra o consumo sobre un material ausente.
- **Qué estaba mal:** mezclaba una consulta de solo lectura con una operación transaccional de negocio. El criterio de aceptación en [docs/requisitos.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/requisitos.md) únicamente exigía errores al registrar compras o descontar consumos.
- **Cómo lo detectaste:** al revisar la tabla de decisión contra el criterio de aceptación (entrada 7 de [bitacora_ia.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/bitacora_ia.md)), comprobé que ninguna regla exigía fallar en una consulta filtrada sin coincidencias.
- **Qué hice:** documenté la ambigüedad, definí que `historial()` devuelve una lista vacía cuando no hay coincidencias y lo dejé respaldado en el docstring de [jy_velas/inventario.py](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/jy_velas/inventario.py), en [registro_pruebas.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/registro_pruebas.md) y en el commit [336eb98](https://github.com/DaizukeGc/jy-velas-jabones/commit/336eb98).

### Caso 2: Persistencia, dependencias y tipos de cantidad

- **Fase:** código.
- **Qué propuso la IA:** persistir las compras en SQLite o con `pandas`, usar `decimal.Decimal` para las cantidades y, en iteraciones posteriores, emplear `assert` en producción o añadir `python-dotenv`.
- **Qué estaba mal:** agregaba dependencias y complejidad fuera del alcance, rompía el `ADR-001` (solo biblioteca estándar) y confundía magnitudes físicas (gramos, mililitros, unidades) con montos monetarios; además, `assert` desaparece con `python -O` y no produce `ErrorInventario`.
- **Cómo lo detectaste:** contrasté las propuestas contra [docs/adr.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/adr.md), el criterio de aceptación y la regla `S101` de Ruff; comprobé que `float` con `pytest.approx` cubría los decimales físicos sin sobrecarga (pytest, 2026).
- **Qué hice:** rechacé SQLite, `pandas`, `Decimal`, `assert` en producción y `python-dotenv`; documenté las decisiones en las entradas 3, 6, 12 y 13 de [bitacora_ia.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/bitacora_ia.md) e implementé el núcleo en biblioteca estándar en el commit [fc085c3](https://github.com/DaizukeGc/jy-velas-jabones/commit/fc085c3).

### Caso 3: Ocho pruebas débiles y verificación por mutaciones

- **Fase:** pruebas.
- **Qué propuso la IA:** aserciones genéricas como `is not None`, `pytest.raises(Exception)`, un esperado de consumo que devolvía `0` al pasarse del stock, una prueba de fecha que esperaba `date.today()` ignorando la fecha explícita y una verificación de mínimo con `<` en lugar de `<=`.
- **Qué estaba mal:** las pruebas habrían pasado aun con la lógica rota porque los esperados se habían inferido del código o eran demasiado permisivos, en lugar de derivarse de la regla de negocio.
- **Cómo lo detectaste:** revisé cada caso contra las particiones, valores límite y tablas de decisión, y ejecuté seis mutaciones intencionales (`M1` a `M6`) sobre `jy_velas/inventario.py` (SHA-256 original y restaurado `55c789b762ca76585c290dca7ef46ddd062d560c45a537c0d69f409bbbb4506d`).
- **Qué hice:** reescribí o descarté las ocho pruebas débiles, consolidé 58 pruebas funcionales parametrizadas en [0c558bf](https://github.com/DaizukeGc/jy-velas-jabones/commit/0c558bf) y registré las mutaciones en [registro_pruebas.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/registro_pruebas.md) y [docs/mutaciones_semana7.txt](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/mutaciones_semana7.txt), commit [336eb98](https://github.com/DaizukeGc/jy-velas-jabones/commit/336eb98):

| Mutación | Cambio introducido en `jy_velas/inventario.py` | ¿Detectada? | Pruebas que fallaron |
|---|---|---|---|
| `M1` | Cambiar `<=` por `<` en la validación de cantidad | Sí | 4 pruebas (compra y consumo con `0` y tablas de decisión) |
| `M2` | Cambiar `>` por `>=` en la validación de stock | Sí | 1 prueba (`consumir_descuenta_existencia[MAT-FRASCO-10-10-0]`) |
| `M3` | Cambiar el descuento por una suma en `consumir_material` | Sí | 4 pruebas de descuento de existencia y tabla de decisión |
| `M4` | Cambiar `<=` por `<` en la alerta de mínimo | Sí | 3 pruebas de límite exacto `5/5` y `0/0` |
| `M5` | Ignorar la fecha personalizada en `registrar_compra` | Sí | 1 prueba (`test_fecha_personalizada_se_conserva`) |
| `M6` | Aceptar `NaN` e infinito (quitar `math.isfinite`) | Sí | 4 pruebas de valores no finitos en compra y consumo |

### Caso 4: Falsos positivos de seguridad, riesgos omitidos y estado mutable

- **Fase:** operación.
- **Qué propuso la IA:** en la auditoría de seguridad señaló tres problemas reales (`H-01` a `H-03`), pero reportó dos falsos positivos: que `math.isfinite` implicaba ejecución dinámica de código y que faltaba hashing seguro de contraseñas con `bcrypt`/`argon2`. Al mismo tiempo, omitió riesgos reales en `Material`, códigos duplicados, referencias mutables y configuración del proyecto.
- **Qué estaba mal:** los dos primeros avisos son falsos positivos (no existe `eval`/`exec`, ni usuarios ni contraseñas), mientras que los riesgos omitidos comprometen la integridad de datos y el control de estado interno (OWASP Foundation, 2021).
- **Cómo lo detectaste:** inspeccioné línea por línea el código frente al commit `fe00949`, ejecuté Ruff y `pip-audit`, y diseñé 58 pruebas de abuso en [tests/test_seguridad_inventario.py](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/tests/test_seguridad_inventario.py) con `bool`, tipos no hashables, `NaN`, longitudes excesivas y códigos duplicados.
- **Qué hice:** descarté los dos falsos positivos, corregí los siete hallazgos reales (`H-01` a `H-07`) añadiendo validaciones en `Material.__post_init__`, rechazo de duplicados en `Inventario.__init__`, copias con `dataclasses.replace` en `materiales_bajo_minimo()`, fijación de `pytest==9.2.0` y configuración de Ruff (`E`, `F`, `B`, `S`), dejando la evidencia en [revision_seguridad.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/revision_seguridad.md) y en el commit [95118b9](https://github.com/DaizukeGc/jy-velas-jabones/commit/95118b9).

## 5. Estado final del sistema

El sistema se entrega como una librería de dominio importable en Python 3.11, sin servidor ni estado oculto: cada regla de negocio vive en una función documentada con docstring y cada falla controlada lanza `ErrorInventario` con un mensaje estable. Esta separación permite que una futura interfaz web o móvil reutilice el mismo contrato sin reescribir la lógica de inventario.

- **Arquitectura:** módulo único de dominio ([jy_velas/inventario.py](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/jy_velas/inventario.py)) usando únicamente `dataclasses`, `datetime`, `math` y `typing`, con datos en memoria. El diseño contempla nueve entidades (`Material`, `Compra`, `Consumo`, `Producto`, `Receta`, `Pedido`, `ItemPedido`, `Venta`, `Cliente`) y trece operaciones; en este incremento se implementaron `Material`, `Compra` y las cinco operaciones del núcleo (`registrar_compra`, `existencia`, `historial`, `consumir_material`, `materiales_bajo_minimo`). Diagramas C4/secuencia y decisiones en [docs/diseno.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/diseno.md) y [docs/adr.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/adr.md).
- **Funcionalidades terminadas:** las tres historias *Must* (`HU-01`, `HU-02` y `HU-03`) están terminadas, con validación previa a cualquier mutación de estado, rechazo de valores no finitos y devolución de copias inmutables.
- **Pruebas y verificación del pipeline:** la suite completa alcanza **116 pruebas parametrizadas** ejecutadas con pytest 9.2.0 (2026). La última ejecución registrada en [docs/pipeline_ultima_ejecucion.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/pipeline_ultima_ejecucion.md) y en [docs/plan_de_pruebas.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/plan_de_pruebas.md) confirma el estado en verde:

| Verificación | Alcance | Resultado observado |
|---|---|---|
| `python -m ruff check .` | Reglas `E`, `F`, `B`, `S` (línea 88) en código y pruebas | `All checks passed!` |
| `python -m pip_audit -r requirements-dev.txt` | Dependencia de desarrollo fijada (`pytest==9.2.0`); cero dependencias de ejecución | `No known vulnerabilities found` |
| `python -m pytest -q` (compras `HU-01`) | [tests/test_registrar_compra.py](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/tests/test_registrar_compra.py) | `21` pruebas superadas |
| `python -m pytest -q` (consumo `HU-02`) | [tests/test_consumir_material.py](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/tests/test_consumir_material.py) | `20` pruebas superadas |
| `python -m pytest -q` (consultas `HU-03`) | [tests/test_consultas_inventario.py](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/tests/test_consultas_inventario.py) | `17` pruebas superadas |
| `python -m pytest -q` (abuso y seguridad) | [tests/test_seguridad_inventario.py](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/tests/test_seguridad_inventario.py) | `58` pruebas superadas |
| **Total del pipeline** | **Suite completa + calidad + auditoría** | **`116 passed in 0.60s`** |

- **Pendientes:** persistencia entre sesiones (`N-09`), módulos de clientes, pedidos, ventas y reportes (`N-06` a `N-08`), interfaz web o móvil (`N-11`), roles multiusuario (`N-10`) e integración continua automatizada de Ruff y `pip-audit` en GitHub. Se difirieron porque no pertenecen a los criterios de aceptación del incremento y porque `ADR-001` prioriza consolidar primero el núcleo de reglas de negocio.

## 6. Reflexión ética y legal

| Principio | Decisión en mi proyecto | Evidencia |
|---|---|---|
| Datos personales (Ley 1581 de 2012) | No hay datos personales reales: la entrevista fue simulada por un compañero y el catálogo usa materiales ficticios con tildes, eñe y apóstrofos («Jabón de avena y ñame «Relámpago»», «Aroma d' naranja»). | [docs/requisitos.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/requisitos.md), [tests/conftest.py](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/tests/conftest.py) |
| Sesgo | El sistema no decide sobre personas ni perfiles crediticios: solo aplica reglas aritméticas deterministas sobre materiales. Rechacé `bool` como cantidad para impedir que `True` se contara como una unidad. | [jy_velas/inventario.py](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/jy_velas/inventario.py), [tests/test_seguridad_inventario.py](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/tests/test_seguridad_inventario.py) |
| Transparencia | Cada error de negocio tiene un mensaje estable y comprensible (`ErrorInventario`); los ADR y la bitácora explican el porqué de cada decisión técnica. | [docs/adr.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/adr.md), [bitacora_ia.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/bitacora_ia.md) |
| Responsabilidad | Yo verifico y respondo por el código entregado; la IA propuso borradores, pero las pruebas, las mutaciones, Ruff y la lectura manual decidieron qué se aceptaba. | [revision_seguridad.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/revision_seguridad.md), [pipeline_ultima_ejecucion.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/pipeline_ultima_ejecucion.md) |
| Propiedad intelectual y política de uso | Código propio con fines académicos; uso del asistente declarado entrada por entrada y decisiones rechazadas documentadas con trazabilidad a commits. | [README.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/README.md), [bitacora_ia.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/bitacora_ia.md) |

El dilema ético más importante que enfrenté fue aceptar o no las pruebas generadas inicialmente por la IA. Resultaba tentador conservar la suite tal como salió, con decenas de aserciones en verde que ahorraban tiempo de entrega; sin embargo, ocho de ellas comprobaban únicamente que no hubiera excepción genérica o que el resultado no fuera nulo, e incluso validaban un consumo excesivo devolviendo cero o ignorando la fecha explícita. Si las hubiera dejado, habría entregado evidencia engañosa de un sistema que corrompía el stock en casos límite. Decidí borrarlas, derivar los esperados directamente desde los criterios de aceptación y aplicar seis mutaciones para demostrar que la suite fallaba cuando el código se rompía. La responsabilidad técnica y ética de ese juicio fue mía, no del asistente.

## 7. Aprendizajes

A lo largo de los seis módulos aprendí a redactar un contrato verificable antes de pedir código, a derivar casos de prueba desde particiones de equivalencia, valores límite y tablas de decisión, a usar mutaciones para comprobar la eficacia real de una suite y a integrar análisis estático (`ruff`) y auditoría de dependencias (`pip-audit`) como filtros objetivos. Al principio confié demasiado en las propuestas iniciales de la IA: acepté sin cuestionar suficiente el uso de `Decimal` y una versión temprana que sumaba la cantidad comprada antes de validarla. También comprobé que un falso positivo de seguridad consume tiempo si no se contrasta con el código real, mientras que un riesgo verdadero (como referencias mutables o códigos duplicados) suele quedar justo donde el asistente no miró. En un próximo proyecto haría tres cosas distinto:

- Escribiría la tabla de casos límite y ambigüedades antes de pedir la implementación, asegurando que cada esperado salga de la regla y no del código generado.
- Integraría Ruff y `pip-audit` desde la primera semana dentro del ciclo habitual de trabajo, no únicamente en la etapa final de operación.
- Exigiría a la IA explicitar sus supuestos técnicos antes de aceptar una sugerencia arquitectónica o de tipos, evitando así desvíos tempranos como `Decimal` o validaciones en orden incorrecto.

## 8. Anexos

### Enlaces a evidencias del repositorio

- Bitácora completa de uso de IA (14 entradas): [bitacora_ia.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/bitacora_ia.md).
- Propuesta (Módulo 1) y requisitos (Módulo 2): [docs/propuesta.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/propuesta.md), [docs/requisitos.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/requisitos.md).
- Diseño (Módulo 3) y decisiones arquitectónicas (ADR): [docs/diseno.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/diseno.md), [docs/adr.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/adr.md).
- Código fuente y pruebas (Módulos 4 y 5): [jy_velas/inventario.py](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/jy_velas/inventario.py), [tests/](https://github.com/DaizukeGc/jy-velas-jabones/tree/main/tests).
- Plan de pruebas, registro formal y mutaciones: [docs/plan_de_pruebas.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/plan_de_pruebas.md), [registro_pruebas.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/registro_pruebas.md), [docs/mutaciones_semana7.txt](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/mutaciones_semana7.txt).
- Seguridad, despliegue y operación (Módulo 6): [revision_seguridad.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/revision_seguridad.md), [docs/despliegue.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/despliegue.md), [docs/operacion.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/operacion.md).
- Última ejecución del pipeline: [docs/pipeline_ultima_ejecucion.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/pipeline_ultima_ejecucion.md).

### Anexo A. Resumen cuantitativo de la bitácora de IA

| Etapa documentada | Entradas | Aceptadas | Aceptadas con cambios | Rechazadas |
|---|---|---|---|---|
| Semana 5 (Módulo 4 — `HU-01`) | Entradas 1 a 6 | 2 | 2 | 2 |
| Semana 7 (Módulo 5 — Pruebas y mutaciones) | Entradas 7 a 10 | 1 | 3 | 0 |
| Semana 6 (Módulo 6 — Seguridad e informe) | Entradas 11 a 14 | 0 | 2 | 2 |
| **Total registrado** | **14 entradas** | **3** | **7** | **4** |

### Anexo B. Síntesis de los siete hallazgos de seguridad corregidos (`95118b9`)

| Id | Origen | Riesgo mitigado y categoría OWASP | Corrección aplicada |
|---|---|---|---|
| `H-01` | IA + verificación manual | Aceptación de `bool` y `TypeError` en `_validar_cantidad` (`A03:2021`) | Comprobación explícita de `(int, float)` excluyendo `bool` y exigiendo `math.isfinite` |
| `H-02` | IA + verificación manual | Falta de validación de tipo en `fecha` (`A04:2021`) | Nuevo método `_validar_fecha` que solo admite `None` o `datetime.date` |
| `H-03` | IA + verificación manual | Códigos no hashables o desbordados en `_buscar_material` (`A03:2021` / `A04:2021`) | Validación de `str` no vacío con longitud máxima de 50 caracteres |
| `H-04` | Inspección manual | `Material` permitía existencia o mínimo negativos o no finitos (`A04:2021`) | Validación en `Material.__post_init__` de tipos, finitud y límites de longitud |
| `H-05` | Inspección manual | `Inventario.__init__` sobrescribía códigos duplicados en silencio (`A04:2021`) | Detección temprana de duplicados con `ErrorInventario` |
| `H-06` | Inspección manual | `materiales_bajo_minimo` devolvía referencias mutables (`A01:2021`) | Devolución de copias independientes con `dataclasses.replace` |
| `H-07` | Inspección manual + Ruff | Falta de configuración de Ruff, `pytest>=8.0` sin fijar y líneas `E501` (`A06:2021`) | Reglas `E,F,B,S` en `pyproject.toml`, `pytest==9.2.0` fijado y líneas divididas |

## Referencias

Fundación Escuela Tecnológica de Neiva. (2026). *Proyecto integrador: tarea final del seminario* [Documento del curso].

García Coqueco, J. S. (2026). *JY Velas y Jabones* [Repositorio de código]. GitHub. https://github.com/DaizukeGc/jy-velas-jabones

Myers, G. J., Sandler, C., & Badgett, T. (2011). *The art of software testing* (3.ª ed.). John Wiley & Sons.

OpenCode. (2026). *Documentación de OpenCode*. https://opencode.ai

OWASP Foundation. (2021). *OWASP Top 10:2021*. https://owasp.org/Top10/

Pressman, R. S., & Maxim, B. R. (2015). *Software engineering: A practitioner's approach* (8.ª ed.). McGraw-Hill Education.

pytest. (2026). *pytest documentation* (Versión 9.2.0). https://docs.pytest.org/

Python Packaging Authority. (2026). *pip-audit* [Paquete de PyPI]. https://pypi.org/project/pip-audit/

Python Software Foundation. (2026). *Python 3.11 documentation*. https://docs.python.org/3.11/

Ruff. (2026). *Ruff documentation*. https://docs.astral.sh/ruff/
