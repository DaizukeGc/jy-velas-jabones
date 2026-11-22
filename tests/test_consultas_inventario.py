"""Pruebas de las consultas de inventario: existencia, historial y alertas.

Las consultas también tienen reglas de negocio: ``existencia`` valida el
catálogo y ``materiales_bajo_minimo`` usa el borde ``existencia <= minimo``.
"""

from __future__ import annotations

import pytest

from jy_velas.inventario import ErrorInventario, Inventario, Material


@pytest.mark.parametrize(
    "codigo, esperado",
    [
        ("MAT-CERA", 800),
        ("MAT-FRASCO", 10),
        ("MAT-ESENCIA", 0),
        # Caso difícil: material con nombre vacío y existencia cero
        ("MAT-SIN-NOMBRE", 0),
    ],
)
def test_existencia_devuelve_el_valor_del_catalogo(
    catalogo_sintetico, codigo, esperado
) -> None:
    assert catalogo_sintetico.existencia(codigo) == pytest.approx(esperado)


@pytest.mark.parametrize(
    "codigo",
    [
        "MAT-AROMA",
        "MAT-INEXISTENTE",
        "",
    ],
)
def test_existencia_material_no_registrado_lanza_error(
    catalogo_sintetico, codigo
) -> None:
    with pytest.raises(ErrorInventario) as error:
        catalogo_sintetico.existencia(codigo)

    assert str(error.value) == f"El material '{codigo}' no está registrado"


def test_historial_vacio_al_inicio(catalogo_sintetico) -> None:
    assert catalogo_sintetico.historial() == []


def test_historial_sin_filtro_devuelve_todas_en_orden(catalogo_sintetico) -> None:
    primera = catalogo_sintetico.registrar_compra("MAT-CERA", 2000)
    segunda = catalogo_sintetico.registrar_compra("MAT-FRASCO", 24)

    assert catalogo_sintetico.historial() == [primera, segunda]


@pytest.mark.parametrize(
    "codigo, esperados",
    [
        ("MAT-CERA", ["MAT-CERA"]),
        ("MAT-FRASCO", ["MAT-FRASCO"]),
        # Ambigüedad documentada: el filtro sin coincidencias devuelve lista vacía
        ("MAT-AROMA", []),
    ],
)
def test_historial_filtra_por_codigo(
    catalogo_sintetico, codigo, esperados
) -> None:
    catalogo_sintetico.registrar_compra("MAT-CERA", 2000)
    catalogo_sintetico.registrar_compra("MAT-FRASCO", 24)

    historial = catalogo_sintetico.historial(codigo)

    assert [compra.codigo_material for compra in historial] == esperados


def test_materiales_bajo_minimo_devuelve_todos_los_que_cumplen(
    catalogo_sintetico,
) -> None:
    codigos = [
        material.codigo for material in catalogo_sintetico.materiales_bajo_minimo()
    ]

    assert codigos == [
        "MAT-FRASCO",
        "MAT-ESENCIA",
        "MAT-JABON",
        "MAT-SIN-NOMBRE",
    ]


@pytest.mark.parametrize(
    "existencia, minimo, incluido",
    [
        # Límite: la existencia igual al mínimo sí genera alerta
        (5, 5, True),
        # Por debajo del mínimo
        (4.99, 5, True),
        # Por encima del mínimo
        (5.01, 5, False),
        # Mínimo cero: solo alerta cuando la existencia llega a cero
        (0, 0, True),
    ],
)
def test_materiales_bajo_minimo_respeta_el_limite(
    existencia, minimo, incluido
) -> None:
    inventario = Inventario(
        [
            Material(
                "MAT-X",
                "Material de prueba",
                "g",
                existencia=existencia,
                minimo=minimo,
            )
        ]
    )

    codigos = [material.codigo for material in inventario.materiales_bajo_minimo()]

    assert codigos == (["MAT-X"] if incluido else [])
