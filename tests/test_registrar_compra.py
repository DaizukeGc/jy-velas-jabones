"""Pruebas de la HU-01: registrar compras de materiales.

Cubren casos normales, casos límite y el escenario de error del criterio
de aceptación (cantidad menor o igual que cero).
"""

from datetime import date

import pytest

from jy_velas.inventario import Compra, ErrorInventario, Inventario, Material


def crear_inventario() -> Inventario:
    """Catálogo de prueba con tres materiales de ejemplo."""
    return Inventario(
        [
            Material("MAT-CERA", "Cera de soja", "g", existencia=800, minimo=500),
            Material("MAT-FRASCO", "Frasco de vidrio", "unidad", existencia=10, minimo=10),
            Material("MAT-ESENCIA", "Esencia de lavanda", "ml", existencia=0, minimo=100),
        ]
    )


# --- Casos normales ---------------------------------------------------------


def test_compra_de_cera_suma_al_inventario() -> None:
    inventario = crear_inventario()

    inventario.registrar_compra("MAT-CERA", 2000)

    assert inventario.existencia("MAT-CERA") == pytest.approx(2800)


def test_compra_de_frascos_suma_al_inventario() -> None:
    inventario = crear_inventario()

    inventario.registrar_compra("MAT-FRASCO", 24)

    assert inventario.existencia("MAT-FRASCO") == pytest.approx(34)


def test_compra_queda_en_el_historial_con_la_fecha_de_hoy() -> None:
    inventario = crear_inventario()

    compra = inventario.registrar_compra("MAT-CERA", 2000)

    assert isinstance(compra, Compra)
    assert compra.codigo_material == "MAT-CERA"
    assert compra.cantidad == pytest.approx(2000)
    assert compra.fecha == date.today()
    assert inventario.historial("MAT-CERA") == [compra]


# --- Casos límite -----------------------------------------------------------


def test_compra_de_una_sola_unidad_es_valida() -> None:
    inventario = crear_inventario()

    inventario.registrar_compra("MAT-CERA", 1)

    assert inventario.existencia("MAT-CERA") == pytest.approx(801)


def test_compra_sobre_material_sin_existencias_es_valida() -> None:
    inventario = crear_inventario()

    inventario.registrar_compra("MAT-ESENCIA", 500)

    assert inventario.existencia("MAT-ESENCIA") == pytest.approx(500)


def test_compra_con_fecha_personalizada_se_guarda_con_esa_fecha() -> None:
    inventario = crear_inventario()
    fecha_de_compra = date(2026, 10, 24)

    compra = inventario.registrar_compra("MAT-CERA", 2000, fecha=fecha_de_compra)

    assert compra.fecha == fecha_de_compra


# --- Casos de error ---------------------------------------------------------


def test_compra_con_cantidad_cero_lanza_error_y_no_cambia_existencias() -> None:
    inventario = crear_inventario()

    with pytest.raises(ErrorInventario) as error:
        inventario.registrar_compra("MAT-CERA", 0)

    assert str(error.value) == "La cantidad debe ser mayor que cero"
    assert inventario.existencia("MAT-CERA") == pytest.approx(800)
    assert inventario.historial() == []


def test_compra_con_cantidad_negativa_lanza_error_y_no_cambia_existencias() -> None:
    inventario = crear_inventario()

    with pytest.raises(ErrorInventario) as error:
        inventario.registrar_compra("MAT-CERA", -500)

    assert str(error.value) == "La cantidad debe ser mayor que cero"
    assert inventario.existencia("MAT-CERA") == pytest.approx(800)
    assert inventario.historial() == []


def test_compra_de_material_no_registrado_lanza_error() -> None:
    inventario = crear_inventario()

    with pytest.raises(ErrorInventario) as error:
        inventario.registrar_compra("MAT-AROMA", 100)

    assert str(error.value) == "El material 'MAT-AROMA' no está registrado"
