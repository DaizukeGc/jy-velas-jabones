# Propuesta del proyecto (Módulo 1)

**Proyecto:** JY Velas y Jabones — núcleo de inventario, pedidos y ventas.
**Estudiante:** Jhonier Santiago García Coqueco.

## Problema

La dueña de una microempresa de velas y jabones artesanales en Neiva lleva el control de los
materiales en hojas de cálculo y apuntes. No puede saber con certeza cuánto stock hay antes de
preparar una tanda y las alertas de reposición llegan tarde.

## Usuario

Dueña-operadora de la microempresa. Necesita registrar compras, descontar consumos y consultar
qué materiales están en su mínimo, sin depender de internet ni de conocimientos técnicos.

## Solución propuesta

Una librería de Python con un catálogo de materiales en memoria, registro de compras, consumo y
consulta de alertas. El primer incremento no incluye base de datos ni interfaz web (ADR-001).
La interfaz podrá construirse después sobre el mismo contrato de `Inventario`.

## Uso previsto de IA

Asistente de código en el IDE (OpenCode) para convertir el problema en contratos, proponer la
estructura de datos y revisar la redacción. Cada sugerencia se contrasta con el criterio de
aceptación y con las pruebas, no se adopta por el hecho de sonar razonable.

## Alcance y criterios de éxito

- Historias HU-01, HU-02 y HU-03 implementadas con TDD.
- Suite de pruebas en verde, linter sin avisos y dependencias auditadas.
- Informe final con una evidencia enlazada por cada fase del ciclo de vida.

## Evidencia

- [`../bitacora_ia.md`](../bitacora_ia.md), entradas 1 a 3.
- [`../README.md`](../README.md), sección «Qué es».
