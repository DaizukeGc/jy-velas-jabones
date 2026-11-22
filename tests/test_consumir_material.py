"""Pruebas de la regla de consumo de materiales (semana 7).

La operación combina tres condiciones: material registrado, cantidad finita
positiva y cantidad menor o igual que la existencia disponible. La tabla de
decisión completa está en ``registro_pruebas.md``.
"""

from __future__ import annotations

import pytest

from jy_velas.inventario import ErrorInventario

MENSAJE_CANTIDAD = "La cantidad debe ser mayor que cero"


def mensaje_stock(codigo: str, disponible: float, solicitado: float) -> str:
    """Construye el mensaje exacto de stock insuficiente."""
    return (
        f"No hay existencia suficiente de '{codigo}': "
        f"disponible {float(disponible):g}, solicitado {float(solicitado):g}"
    )


@pytest.mark.parametrize(
    "codigo, cantidad, inicial, esperado",
    [
        # R1: consumo típico con existencia positiva
        ("MAT-CERA", 500, 800, 300),
        # R1 en el límite superior permitido: consumir toda la existencia
        ("MAT-FRASCO", 10, 10, 0),
        # R1 en el límite inferior positivo
        ("MAT-CERA", 1, 800, 799),
    ],
)
def test_consumir_descuenta_existencia(
    catalogo_sintetico, codigo, cantidad, inicial, esperado
) -> None:
    assert catalogo_sintetico.existencia(codigo) == pytest.approx(inicial)

    resultado = catalogo_sintetico.consumir_material(codigo, cantidad)

    assert resultado == pytest.approx(esperado)
    assert catalogo_sintetico.existencia(codigo) == pytest.approx(esperado)


@pytest.mark.parametrize(
    "codigo, cantidad, inicial",
    [
        # R2: un gramo más que la existencia disponible
        ("MAT-CERA", 801, 800),
        # R2: existencia en cero
        ("MAT-ESENCIA", 1, 0),
        # R2: exceso fraccionario sobre la existencia
        ("MAT-FRASCO", 10.01, 10),
    ],
)
def test_consumir_mas_que_existencia_lanza_error(
    catalogo_sintetico, codigo, cantidad, inicial
) -> None:
    with pytest.raises(ErrorInventario) as error:
        catalogo_sintetico.consumir_material(codigo, cantidad)

    assert str(error.value) == mensaje_stock(codigo, inicial, cantidad)
    assert catalogo_sintetico.existencia(codigo) == pytest.approx(inicial)


@pytest.mark.parametrize(
    "cantidad",
    [
        0,
        -1,
        -0.01,
        float("nan"),
        float("inf"),
        float("-inf"),
    ],
)
def test_consumir_cantidad_no_positiva_lanza_error(
    catalogo_sintetico, cantidad
) -> None:
    with pytest.raises(ErrorInventario) as error:
        catalogo_sintetico.consumir_material("MAT-CERA", cantidad)

    assert str(error.value) == MENSAJE_CANTIDAD
    assert catalogo_sintetico.existencia("MAT-CERA") == pytest.approx(800)


@pytest.mark.parametrize(
    "codigo",
    [
        "MAT-AROMA",
        "MAT-INEXISTENTE",
        "",
    ],
)
def test_consumir_material_no_registrado_lanza_error(
    catalogo_sintetico, codigo
) -> None:
    with pytest.raises(ErrorInventario) as error:
        catalogo_sintetico.consumir_material(codigo, 1)

    assert str(error.value) == f"El material '{codigo}' no está registrado"
    assert catalogo_sintetico.existencia("MAT-CERA") == pytest.approx(800)


@pytest.mark.parametrize(
    "codigo, cantidad, resultado",
    [
        # R1: registrado, positiva y dentro del stock -> descuenta
        ("MAT-CERA", 1, "ok"),
        # R2: registrado, positiva y sobre el stock -> error de stock
        ("MAT-CERA", 801, "stock"),
        # R3: registrado, no positiva -> error de cantidad
        ("MAT-CERA", 0, "cantidad"),
        # R4: no registrado y positiva -> error de material
        ("MAT-AROMA", 1, "material"),
        # R5: no registrado y no positiva -> prioridad del material
        ("MAT-AROMA", 0, "material"),
    ],
)
def test_tabla_decision_consumir_material(
    catalogo_sintetico, codigo, cantidad, resultado
) -> None:
    if resultado == "ok":
        restante = catalogo_sintetico.consumir_material(codigo, cantidad)
        assert restante == pytest.approx(799)
        assert catalogo_sintetico.existencia(codigo) == pytest.approx(799)
    else:
        with pytest.raises(ErrorInventario) as error:
            catalogo_sintetico.consumir_material(codigo, cantidad)
        if resultado == "stock":
            assert str(error.value) == mensaje_stock(codigo, 800, cantidad)
        elif resultado == "cantidad":
            assert str(error.value) == MENSAJE_CANTIDAD
        else:
            assert str(error.value) == f"El material '{codigo}' no está registrado"
        assert catalogo_sintetico.existencia("MAT-CERA") == pytest.approx(800)
