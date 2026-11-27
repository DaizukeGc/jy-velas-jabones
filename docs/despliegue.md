# Guía de despliegue (Módulo 6)

El proyecto es una librería local: no hay servidor, base de datos ni servicios externos.

## Preparación

```bash
git clone https://github.com/DaizukeGc/jy-velas-jabones.git
cd jy-velas-jabones
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

## Verificación antes de usar

```bash
python -m ruff check .
python -m pip_audit -r requirements-dev.txt
python -m pytest -q
```

Los tres comandos deben terminar sin errores. La salida real de la última ejecución está en
[`pipeline_ultima_ejecucion.md`](pipeline_ultima_ejecucion.md).

## Uso

```python
from jy_velas.inventario import Inventario, Material

inventario = Inventario([Material("MAT-CERA", "Cera de soja", "g", 800, 500)])
inventario.registrar_compra("MAT-CERA", 2000)
```

## Cambio y reversión

Cada cambio se verifica con la suite completa. Si una ejecución falla, se revierte el commit
con `git revert` y se vuelve a ejecutar el pipeline. No hay migraciones de base de datos.

## Evidencia

- [`../README.md`](../README.md), secciones «Instalación» y «Ejecución».
- [`../pyproject.toml`](../pyproject.toml) y [`../requirements-dev.txt`](../requirements-dev.txt).
