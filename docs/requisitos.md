# Requisitos (Módulo 2)

La entrevista de levantamiento se hizo con un compañero que simuló el papel de la dueña de JY
Velas y Jabones. Las citas son reconstruidas de esa sesión; no hay datos de personas reales.
El cuestionario tuvo nueve preguntas sobre inventario, compras, consumos, alertas, pedidos,
ventas, generación de reportes, acceso multiusuario y persistencia.

## Necesidades relevadas

| Id | Necesidad | Prioridad |
|---|---|---|
| N-01 | Saber cuánto material hay disponible antes de una tanda | Must |
| N-02 | Registrar las compras de materiales con fecha | Must |
| N-03 | Descontar los materiales consumidos en una tanda | Must |
| N-04 | Ver qué materiales están en o por debajo de su mínimo | Must |
| N-05 | Consultar el historial de compras por material | Should |
| N-06 | Registrar clientes y pedidos | Should |
| N-07 | Registrar ventas y productos terminados | Should |
| N-08 | Generar reportes de consumo y reposición | Could |
| N-09 | Persistir la información entre sesiones | Could |
| N-10 | Permitir varios usuarios con roles | Won't (por ahora) |
| N-11 | Acceder desde el celular | Won't (por ahora) |

## Historias de usuario del incremento

| Id | Historia | Criterio de aceptación principal | Estado |
|---|---|---|---|
| HU-01 | Como dueña, quiero registrar compras de materiales para saber cuánto tengo | Suma la cantidad a la existencia y guarda `Compra` con fecha de hoy | Terminada |
| HU-02 | Como dueña, quiero descontar los materiales que uso en una tanda | Descuenta solo si hay stock suficiente; si no, no modifica el inventario | Terminada |
| HU-03 | Como dueña, quiero ver los materiales en su mínimo | Lista `existencia <= minimo` en el orden del catálogo | Terminada |

## Escenarios Gherkin (HU-01)

```gherkin
Escenario 1: compra normal de cera
  Dado que hay 800 g de "Cera de soja"
  Cuando registro la compra de 2000 g
  Entonces el inventario queda en 2800 g
  Y la compra aparece en el historial con la fecha de hoy

Escenario 2: cantidad inválida
  Dado que hay 800 g de "Cera de soja"
  Cuando intento registrar una compra de -500 g
  Entonces el sistema no la guarda
  Y muestra "La cantidad debe ser mayor que cero"
  Y el inventario sigue en 800 g
```

## Requisitos no funcionales

| Id | Requisito |
|---|---|
| RNF-01 | Sin dependencias de ejecución: solo biblioteca estándar de Python 3.11. |
| RNF-02 | Cada operación falla con `ErrorInventario` y deja el estado sin cambios. |
| RNF-03 | Los códigos de material son cadenas no vacías de hasta 50 caracteres. |
| RNF-04 | Las cantidades son números finitos estrictamente positivos. |
| RNF-05 | Ningún dato personal real en código, pruebas ni documentación. |

## Trazabilidad y MoSCoW

Las 11 necesidades se cubren con 10 historias de usuario; las tres historias Must son HU-01,
HU-02 y HU-03 (50 % del conjunto Must/Should implementado en este incremento). La matriz de
trazabilidad completa está en el informe de requisitos de la semana 3.

## Evidencia

- [`../bitacora_ia.md`](../bitacora_ia.md), entradas 1 a 4 y 7.
- [`registro_pruebas.md`](../registro_pruebas.md), tablas de decisión derivadas de estos criterios.
