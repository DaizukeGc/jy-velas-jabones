# Última ejecución del pipeline — 2026-11-26

Ejecutado en la raíz del repositorio con Python 3.11.0. Los tres comandos terminaron
sin errores.

## 1. Linter

```text
$ python -m ruff check .
All checks passed!
```

Reglas activas: `E`, `F`, `B`, `S` (ver `../pyproject.toml`). `S101` se ignora solo en
`tests/*`; `E501` y `S607` se ignoran solo en el script heredado
`docs/generar_informe.py`.

## 2. Dependencias

```text
$ python -m pip_audit -r requirements-dev.txt
No known vulnerabilities found
```

## 3. Pruebas

```text
$ python -m pytest -q
============================= test session starts =============================
platform win32 -- Python 3.11.0, pytest-9.2.0, pluggy-1.7.0
configfile: pyproject.toml
testpaths: tests
collected 116 items

tests\test_consultas_inventario.py .................                     [ 14%]
tests\test_consumir_material.py ....................                     [ 31%]
tests\test_registrar_compra.py .....................                     [ 50%]
tests\test_seguridad_inventario.py ..................................... [ 81%]
.....................                                                    [100%]

============================= 116 passed in 0.60s =============================
```

## Evidencia relacionada

- [`../revision_seguridad.md`](../revision_seguridad.md): hallazgos y correcciones.
- [`plan_de_pruebas.md`](plan_de_pruebas.md): estrategia y cobertura.
- [`../bitacora_ia.md`](../bitacora_ia.md): decisiones de IA verificadas.
