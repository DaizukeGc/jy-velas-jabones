"""Datos sintéticos compartidos por la suite de pruebas de la semana 7.

El catálogo es ficticio y está ambientado en JY Velas y Jabones (Neiva). No
contiene datos de personas reales. Incluye casos difíciles: tildes, eñe,
apóstrofo, comillas angulares, nombre vacío y valores en cero.
"""

from __future__ import annotations

import pytest

from jy_velas.inventario import Inventario, Material


@pytest.fixture()
def catalogo_sintetico() -> Inventario:
    """Catálogo nuevo para cada prueba, con seis materiales de ejemplo."""
    return Inventario(
        [
            Material("MAT-CERA", "Cera de soja", "g", existencia=800, minimo=500),
            Material(
                "MAT-FRASCO",
                "Frasco de vidrio",
                "unidad",
                existencia=10,
                minimo=10,
            ),
            Material(
                "MAT-ESENCIA",
                "Esencia de lavanda",
                "ml",
                existencia=0,
                minimo=100,
            ),
            Material(
                "MAT-JABON",
                "Jabón de avena y ñame «Relámpago»",
                "unidad",
                existencia=5,
                minimo=5,
            ),
            Material(
                "MAT-NARANJA",
                "Aroma d' naranja",
                "ml",
                existencia=20,
                minimo=10,
            ),
            Material(
                "MAT-SIN-NOMBRE",
                "",
                "g",
                existencia=0,
                minimo=0,
            ),
        ]
    )
