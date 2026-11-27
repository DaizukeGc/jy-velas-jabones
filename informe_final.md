# Informe final del proyecto integrador

Proyecto: JY Velas y Jabones — núcleo de inventario, pedidos y ventas
Estudiante: Jhonier Santiago García Coqueco
Repositorio: https://github.com/DaizukeGc/jy-velas-jabones
Fecha: 26 de noviembre de 2026

## 1. Resumen

La dueña de una microempresa de velas y jabones artesanales en Neiva no podía saber con certeza cuánto material tenía antes de preparar una tanda: llevaba el control en hojas de cálculo y apuntes. Construí una librería de Python (Python Software Foundation, 2026) que registra compras, descuenta consumos y lista los materiales en su mínimo, con contrato explícito y sin dependencias de ejecución. Usé IA en las seis fases del ciclo de vida: para acotar el problema y la herramienta, extraer requisitos de una entrevista simulada, proponer diagramas y decisiones arquitectónicas, generar el código con TDD, crear particiones y pruebas, y revisar seguridad y dependencias. La verificación fue continua: pruebas en rojo y verde, ocho pruebas débiles corregidas, seis mutaciones que rompieron la suite, linter (Ruff, 2026) y auditoría de dependencias (Python Packaging Authority, 2026). Estado final: 116 pruebas superadas, Ruff sin avisos, pip-audit sin vulnerabilidades y siete hallazgos de seguridad corregidos. El resultado principal no fue que la IA escribiera código, sino que cada salida fue contrastada con una regla, una prueba o una herramienta antes de aceptarla.

**Palabras clave:** inteligencia artificial, ciclo de vida del software, pruebas, seguridad, inventario.

## 2. Problema y usuario

El usuario es la dueña-operadora de JY Velas y Jabones. Antes de este proyecto registraba las entradas de cera, frascos y esencias en una hoja de cálculo y apuntaba los consumos en papel. Cuando llegaba el momento de producir, no tenía una forma confiable de saber si había stock ni qué materiales debía reponer, y las alertas aparecían tarde. Necesitaba tres operaciones simples: registrar una compra con fecha, descontar lo usado en una tanda sin pasarse del stock y consultar qué materiales están en o por debajo de su mínimo.

La propuesta inicial está en [docs/propuesta.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/propuesta.md) y el levantamiento en [docs/requisitos.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/requisitos.md). La entrevista fue simulada por un compañero, declarada así en la bitácora: no se usaron datos de personas reales. De once necesidades y diez historias, las tres Must del incremento son HU-01, HU-02 y HU-03, todas terminadas.

El alcance se limitó a la capa de dominio y a su verificación: no se construyó interfaz, base de datos ni autenticación, porque ninguna de esas piezas aparece en los criterios de aceptación. Esa decisión quedó registrada en los [ADR](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/adr.md) y permitió que la dueña entendiera cada operación sin intermediarios técnicos. La solución se puede ejecutar con un solo comando de Python, como se muestra en la [guía de despliegue](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/despliegue.md).

## 3. La IA en el ciclo de vida

| Módulo y fase | Qué hice con IA | Herramienta | Evidencia (enlace) | Cómo verificaste |
|---|---|---|---|---|
| 1. Fundamentos | Convertir el problema en una propuesta acotada y decidir la herramienta prevista | OpenCode | [propuesta.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/propuesta.md) | Comprobé que el usuario, el problema y el alcance fueran verificables; fijé ADR-001 de solo biblioteca estándar |
| 2. Requisitos | Extraer necesidades, historias y criterios Gherkin de la entrevista simulada | OpenCode | [requisitos.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/requisitos.md), [bitácora entrada 7](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/bitacora_ia.md) | Revisé cada esperado contra la regla y marqué la ambigüedad de `historial()` sin coincidencias |
| 3. Diseño | Proponer contexto C4, secuencia, entidades y decisiones arquitectónicas | OpenCode + Mermaid CLI | [diseno.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/diseno.md), [adr.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/adr.md) | Contrasté los diagramas con el contrato y verifiqué que las nueve entidades y los ADR fueran coherentes con el código |
| 4. Código | Implementar `Inventario`, `Material` y `Compra` con TDD y refactorizar | OpenCode | [inventario.py](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/jy_velas/inventario.py), [commit fc085c3](https://github.com/DaizukeGc/jy-velas-jabones/commit/fc085c3) | Pruebas en rojo primero, verde después; Ruff y docstrings; el orden de validación se corrigió con una prueba |
| 5. Pruebas | Generar particiones, valores límite, tablas de decisión y la suite parametrizada | OpenCode | [registro_pruebas.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/registro_pruebas.md), [tests/](https://github.com/DaizukeGc/jy-velas-jabones/tree/main/tests) | Descarté ocho pruebas débiles, apliqué seis mutaciones y dejé 116 pruebas en verde |
| 6. Operación | Revisar seguridad, configurar linter, auditar dependencias y documentar despliegue | OpenCode + Ruff (2026) + pip-audit (Python Packaging Authority, 2026) | [revision_seguridad.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/revision_seguridad.md), [pipeline](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/pipeline_ultima_ejecucion.md) | Tres hallazgos de la IA eran falsos positivos; la revisión manual añadió tres hallazgos reales y el pipeline quedó en verde |

## 4. Verificación: lo que la IA hizo mal y cómo lo encontraste

### Caso 1: El histórico de un código inexistente

- **Fase:** requisitos.
- **Qué propuso la IA:** que `historial(codigo_inexistente)` lanzara `ErrorInventario`, igual que una compra sobre un material ausente.
- **Qué estaba mal:** mezclaba una consulta con una operación de negocio. El criterio de aceptación solo hablaba de errores al registrar compras o consumir.
- **Cómo lo detectaste:** al revisar la tabla de decisión contra el criterio, noté que ninguna regla exigía fallar en una consulta.
- **Qué hice:** documenté la ambigüedad y decidí que devuelve lista vacía; quedó registrado en [registro_pruebas.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/registro_pruebas.md) y con su prueba, en el commit [336eb98](https://github.com/DaizukeGc/jy-velas-jabones/commit/336eb98).

### Caso 2: Persistencia y tipos de cantidad

- **Fase:** código.
- **Qué propuso la IA:** guardar las compras en SQLite o con pandas, y usar `decimal.Decimal` para las cantidades.
- **Qué estaba mal:** agregaba dependencias y complejidad sin que el contrato lo pidiera, y rompía el ADR-001. Las cantidades son magnitudes físicas, no dinero.
- **Cómo lo detectaste:** comparé el ADR con el criterio de aceptación y comprobé que `pytest.approx` ya cubría los decimales de las pruebas (pytest, 2026).
- **Qué hice:** rechacé ambas sugerencias, dejé solo la biblioteca estándar y documenté la decisión en las entradas 3 y 6 de [bitacora_ia.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/bitacora_ia.md); implementación en el commit [fc085c3](https://github.com/DaizukeGc/jy-velas-jabones/commit/fc085c3).

### Caso 3: Ocho pruebas débiles

- **Fase:** pruebas.
- **Qué propuso la IA:** aserciones como `is not None`, `pytest.raises(Exception)`, un esperado de consumo que devolvía cero al pasarse del stock, una prueba de fecha que ignoraba la fecha explícita y un mínimo con `<` en vez de `<=`.
- **Qué estaba mal:** habrían pasado aunque el código estuviera equivocado; el esperado salía del código y no de la regla.
- **Cómo lo detectaste:** revisé cada prueba contra la tabla de decisión y ejecuté seis mutaciones (M1 a M6); las pruebas corregidas fallaron con todas ellas.
- **Cómo lo corregí:** reescribí los esperados desde la regla, conservé 58 casos y documenté el proceso en [registro_pruebas.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/registro_pruebas.md) y [mutaciones_semana7.txt](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/mutaciones_semana7.txt), commits [0c558bf](https://github.com/DaizukeGc/jy-velas-jabones/commit/0c558bf) y [336eb98](https://github.com/DaizukeGc/jy-velas-jabones/commit/336eb98).

### Caso 4: Falsos positivos de seguridad y estado mutable

- **Fase:** operación.
- **Qué propuso la IA:** que `math.isfinite` era ejecución dinámica de código y que faltaba hashing de contraseñas con bcrypt/argon2. No detectó los códigos duplicados ni que `materiales_bajo_minimo` devolviera referencias mutables.
- **Qué estaba mal:** los dos primeros son falsos positivos (no hay `eval`, ni usuarios ni contraseñas); los otros dos son riesgos reales de integridad (OWASP Foundation, 2021).
- **Cómo lo detectaste:** leí línea por línea contra el commit `fe00949`, ejecuté Ruff y escribí 58 pruebas de abuso con tipos inválidos, `NaN`, longitudes excesivas y duplicados.
- **Qué hice:** descarté los falsos positivos, corregí siete hallazgos y dejé la evidencia en [revision_seguridad.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/revision_seguridad.md) y [test_seguridad_inventario.py](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/tests/test_seguridad_inventario.py), commit [95118b9](https://github.com/DaizukeGc/jy-velas-jabones/commit/95118b9).

## 5. Estado final del sistema

El sistema se entrega como una librería importable, no como un servidor: cada regla vive en una función con docstring y cada error de negocio tiene un mensaje estable. Eso permite que una futura interfaz web o móvil reutilice el mismo contrato sin reescribir la lógica, y facilita que cualquier línea del código pueda explicarse en la sustentación.

- **Arquitectura:** librería Python de un solo módulo de dominio (`jy_velas/inventario.py`), sin dependencias de ejecución, con datos en memoria y contrato reutilizable por una futura interfaz. Diagramas y ADR en [diseno.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/diseno.md) y [adr.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/adr.md).
- **Funcionalidades terminadas:** HU-01 registrar compras, HU-02 consumir materiales y HU-03 alertas de mínimo. Las tres historias Must del incremento están completas; las demás del levantamiento quedan para iteraciones posteriores.
- **Pruebas:** 116 pruebas parametrizadas (21 + 20 + 17 + 58) ejecutadas con pytest (2026). Última ejecución en [pipeline_ultima_ejecucion.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/pipeline_ultima_ejecucion.md): 116 passed, Ruff sin avisos y pip-audit sin vulnerabilidades. Cobertura de reglas de negocio y abuso en [plan_de_pruebas.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/plan_de_pruebas.md).
- **Pendientes:** persistencia entre sesiones (N-09), interfaz web o móvil, roles de usuario e integración continua de Ruff y pip-audit. Se difirieron porque no están en el criterio de aceptación de este incremento y porque el ADR-001 prioriza un núcleo simple.

## 6. Reflexión ética y legal

| Principio | Decisión en mi proyecto | Evidencia |
|---|---|---|
| Datos personales (Ley 1581 de 2012) | No hay datos personales reales: la entrevista fue simulada por un compañero y el catálogo usa materiales ficticios con tildes y apóstrofos | [requisitos.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/requisitos.md), [conftest.py](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/tests/conftest.py) |
| Sesgo | El sistema no decide sobre personas: solo aplica reglas numéricas a materiales. Rechacé `bool` como cantidad para evitar que `True` se contara como una unidad | [inventario.py](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/jy_velas/inventario.py), [test_seguridad_inventario.py](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/tests/test_seguridad_inventario.py) |
| Transparencia | Cada error de negocio tiene un mensaje estable y explicable; los ADR y la bitácora explican por qué se tomó cada decisión | [adr.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/adr.md), [bitacora_ia.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/bitacora_ia.md) |
| Responsabilidad | Yo verifico y respondo por el código; la IA propuso, pero las pruebas, el linter y la lectura manual decidieron qué se aceptaba | [revision_seguridad.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/revision_seguridad.md), [pipeline](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/pipeline_ultima_ejecucion.md) |
| Propiedad intelectual y política de uso | Código propio con fines académicos, licencia declarada en el README; uso de IA declarado entrada por entrada | [README.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/README.md), [bitacora_ia.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/bitacora_ia.md) |

El dilema más importante fue aceptar o no las pruebas generadas por IA. Era tentador quedarse con 58 pruebas que pasaban y ahorrar tiempo, pero ocho comprobaban el estado en vez de la regla. Si las hubiera aceptado, el sistema habría parecido correcto con stock insuficiente y fechas ignoradas. Decidí borrarlas, reescribirlas desde el criterio de aceptación y ejecutar mutaciones para demostrar que fallaban cuando el código se rompía. La responsabilidad por ese juicio fue mía, no del asistente.

## 7. Aprendizajes

Aprendí a escribir un contrato antes de pedir código, a derivar pruebas de particiones y tablas de decisión, a ejecutar mutaciones para medir si una prueba sirve y a auditar dependencias con pip-audit. Confié demasiado en la IA al inicio: acepté sin revisar la idea de usar `Decimal` y una primera versión que sumaba la cantidad antes de validarla. También aprendí que un falso positivo puede desperdiciar tiempo y que un hallazgo real puede estar justo donde la IA no miró. Haría tres cosas distinto:

- Escribiría la tabla de casos límite antes de pedir la implementación, para que el esperado viniera de la regla y no del código.
- Dejaría Ruff y pip-audit como parte normal del ciclo desde la primera semana, no al final.
- Pediría a la IA que explique sus supuestos antes de aceptar una sugerencia; así habría detectado antes lo de `Decimal` y el orden de las validaciones.

## 8. Anexos

- Bitácora de uso de IA: [bitacora_ia.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/bitacora_ia.md) (14 entradas).
- Propuesta y requisitos: [propuesta.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/propuesta.md), [requisitos.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/requisitos.md).
- Diseño y ADR: [diseno.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/diseno.md), [adr.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/adr.md).
- Plan de pruebas y mutaciones: [plan_de_pruebas.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/plan_de_pruebas.md), [mutaciones_semana7.txt](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/mutaciones_semana7.txt).
- Seguridad, despliegue y operación: [revision_seguridad.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/revision_seguridad.md), [despliegue.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/despliegue.md), [operacion.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/operacion.md).
- Última ejecución del pipeline: [pipeline_ultima_ejecucion.md](https://github.com/DaizukeGc/jy-velas-jabones/blob/main/docs/pipeline_ultima_ejecucion.md).

## Referencias

Fundación Escuela Tecnológica de Neiva. (2026). *Proyecto integrador: tarea final del seminario* [Documento del curso].

García Coqueco, J. S. (2026). *JY Velas y Jabones* [Repositorio de código]. GitHub. https://github.com/DaizukeGc/jy-velas-jabones

OpenCode. (2026). *Documentación de OpenCode*. https://opencode.ai

OWASP Foundation. (2021). *OWASP Top 10:2021*. https://owasp.org/Top10/

pytest. (2026). *pytest documentation*. https://docs.pytest.org/

Python Packaging Authority. (2026). *pip-audit* [Paquete de PyPI]. https://pypi.org/project/pip-audit/

Python Software Foundation. (2026). *Python 3.11 documentation*. https://docs.python.org/3.11/

Ruff. (2026). *Ruff documentation*. https://docs.astral.sh/ruff/
