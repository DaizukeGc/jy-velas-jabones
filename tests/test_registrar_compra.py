"""Pruebas de la HU-01: registrar compras de materiales.

Cada fila de ``parametrize`` corresponde a una partición, un valor límite o una
regla de la tabla de decisión documentada en ``registro_pruebas.md``.
"""

from __future__ import annotations

from datetime import date

import pytest

from jy_velas.inventario import Compra, ErrorInventario

MENSAJE_CANTIDAD = "La cantidad debe ser mayor que cero"


@pytest.mark.parametrize(
    "codigo, cantidad, inicial, esperado",
    [
        # EP-Q1 / EP-C1 / EP-E1: compra típica sobre existencia positiva
        ("MAT-CERA", 2000, 800, 2800),
        # EP-Q1 / EP-C1 / EP-E1: otra unidad y otro material
        ("MAT-FRASCO", 24, 10, 34),
        # Límite inferior válido: la menor cantidad positiva entera
        ("MAT-CERA", 1, 800, 801),
        # EP-E2: existencia inicial en cero
        ("MAT-ESENCIA", 500, 0, 500),
        # Límite positivo fraccionario: 0.5 es mayor que cero
        ("MAT-CERA", 0.5, 800, 800.5),
    ],
)
def test_registrar_compra_suma_a_la_existencia(
    catalogo_sintetico, codigo, cantidad, inicial, esperado
) -> None:
    assert catalogo_sintetico.existencia(codigo) == pytest.approx(inicial)

    catalogo_sintetico.registrar_compra(codigo, cantidad)

    assert catalogo_sintetico.existencia(codigo) == pytest.approx(esperado)


@pytest.mark.parametrize(
    "cantidad",
    [
        # EP-Q2: el cero es el límite inferior inválido
        0,
        # EP-Q3: enteros negativos, incluido el adyacente al límite
        -1,
        -500,
        # EP-Q3: negativo fraccionario
        -0.01,
        # Partición inválida: NaN no es mayor que cero
        float("nan"),
        # Partición inválida: infinito no es una cantidad física válida
        float("inf"),
        float("-inf"),
    ],
)
def test_cantidad_no_positiva_lanza_error_y_no_cambia_nada(
    catalogo_sintetico, cantidad
) -> None:
    with pytest.raises(ErrorInventario) as error:
        catalogo_sintetico.registrar_compra("MAT-CERA", cantidad)

    assert str(error.value) == MENSAJE_CANTIDAD
    assert catalogo_sintetico.existencia("MAT-CERA") == pytest.approx(800)
    assert catalogo_sintetico.historial() == []


@pytest.mark.parametrize(
    "codigo",
    [
        # EP-C2: código con formato válido pero ausente del catálogo
        "MAT-AROMA",
        "MAT-INEXISTENTE",
        # Caso difícil: cadena vacía
        "",
    ],
)
def test_material_no_registrado_lanza_error(catalogo_sintetico, codigo) -> None:
    with pytest.raises(ErrorInventario) as error:
        catalogo_sintetico.registrar_compra(codigo, 100)

    assert str(error.value) == f"El material '{codigo}' no está registrado"
    assert catalogo_sintetico.historial() == []


def test_fecha_personalizada_se_conserva(catalogo_sintetico) -> None:
    fecha_de_compra = date(2026, 10, 24)

    compra = catalogo_sintetico.registrar_compra(
        "MAT-CERA", 2000, fecha=fecha_de_compra
    )

    assert isinstance(compra, Compra)
    assert compra.codigo_material == "MAT-CERA"
    assert compra.cantidad == pytest.approx(2000)
    assert compra.fecha == fecha_de_compra
    assert catalogo_sintetico.historial("MAT-CERA") == [compra]


def test_fecha_por_defecto_es_hoy(catalogo_sintetico) -> None:
    compra = catalogo_sintetico.registrar_compra("MAT-CERA", 2000)

    assert compra.fecha == date.today()


@pytest.mark.parametrize(
    "codigo, cantidad, mensaje_error",
    [
        # R1: material registrado y cantidad positiva -> se registra
        ("MAT-CERA", 1, None),
        # R2: material registrado y cantidad no positiva -> error de cantidad
        ("MAT-CERA", 0, MENSAJE_CANTIDAD),
        # R3: material no registrado y cantidad positiva -> error de material
        ("MAT-AROMA", 1, "El material 'MAT-AROMA' no está registrado"),
        # R4: material no registrado y cantidad no positiva -> prioridad del material
        ("MAT-AROMA", 0, "El material 'MAT-AROMA' no está registrado"),
    ],
)
def test_tabla_decision_registrar_compra(
    catalogo_sintetico, codigo, cantidad, mensaje_error
) -> None:
    if mensaje_error is None:
        compra = catalogo_sintetico.registrar_compra(codigo, cantidad)
        assert compra.codigo_material == codigo
        assert compra.cantidad == pytest.approx(cantidad)
        assert catalogo_sintetico.historial(codigo) == [compra]
    else:
        with pytest.raises(ErrorInventario) as error:
            catalogo_sintetico.registrar_compra(codigo, cantidad)
        assert str(error.value) == mensaje_error
        assert catalogo_sintetico.historial() == []
