"""Pruebas de abuso de la API interna del inventario (semana 6).

Cubren entradas que un llamador descuidado o malintencionado podría enviar:
tipos incorrectos, valores no finitos o negativos, longitudes excesivas,
fechas inválidas y códigos duplicados. Comprueban que el sistema falla con
``ErrorInventario`` y que no deja el estado a medias.
"""

from __future__ import annotations

import pytest

from jy_velas.inventario import ErrorInventario, Inventario, Material

MENSAJE_CODIGO = "El código del material debe ser una cadena no vacía"
MENSAJE_LONGITUD = (
    "El código, el nombre o la unidad superan la longitud permitida"
)
MENSAJE_VALOR = "La existencia y el mínimo deben ser números finitos no negativos"
MENSAJE_DUPLICADO = "El material '{codigo}' está duplicado en el catálogo"
MENSAJE_CANTIDAD = "La cantidad debe ser mayor que cero"
MENSAJE_MATERIAL = "El material '{codigo}' no está registrado"
MENSAJE_FECHA = "La fecha de la compra debe ser una fecha válida"


def _material(**cambios) -> Material:
    """Construye un material válido y aplica los cambios indicados."""
    datos = {
        "codigo": "MAT-X",
        "nombre": "Material de prueba",
        "unidad": "g",
        "existencia": 10.0,
        "minimo": 5.0,
    }
    datos.update(cambios)
    return Material(**datos)


@pytest.mark.parametrize("codigo", ["", 123, None])
def test_material_rechaza_codigo_invalido(codigo) -> None:
    with pytest.raises(ErrorInventario) as error:
        _material(codigo=codigo)
    assert str(error.value) == MENSAJE_CODIGO


@pytest.mark.parametrize(
    "nombre, unidad",
    [(123, "g"), ("Material", 123), (None, "g"), ("Material", None)],
)
def test_material_rechaza_nombre_o_unidad_no_texto(nombre, unidad) -> None:
    with pytest.raises(ErrorInventario) as error:
        _material(nombre=nombre, unidad=unidad)
    assert str(error.value) == MENSAJE_CODIGO


@pytest.mark.parametrize(
    "cambios",
    [
        {"codigo": "X" * 51},
        {"nombre": "N" * 101},
        {"unidad": "U" * 21},
    ],
)
def test_material_rechaza_longitudes_excesivas(cambios) -> None:
    with pytest.raises(ErrorInventario) as error:
        _material(**cambios)
    assert str(error.value) == MENSAJE_LONGITUD


@pytest.mark.parametrize(
    "campo, valor",
    [
        ("existencia", -1),
        ("existencia", float("nan")),
        ("existencia", float("inf")),
        ("existencia", True),
        ("minimo", -1),
        ("minimo", float("nan")),
        ("minimo", float("inf")),
        ("minimo", True),
    ],
)
def test_material_rechaza_valores_no_finitos_o_negativos(campo, valor) -> None:
    with pytest.raises(ErrorInventario) as error:
        _material(**{campo: valor})
    assert str(error.value) == MENSAJE_VALOR


@pytest.mark.parametrize(
    "cambios",
    [
        {"codigo": "X" * 50},
        {"nombre": "N" * 100},
        {"unidad": "U" * 20},
        {"existencia": 0, "minimo": 0},
    ],
)
def test_material_acepta_los_limites_validos(cambios) -> None:
    material = _material(**cambios)
    assert isinstance(material, Material)


def test_inventario_rechaza_codigos_duplicados() -> None:
    with pytest.raises(ErrorInventario) as error:
        Inventario(
            [
                _material(codigo="MAT-REPETIDO"),
                _material(codigo="MAT-REPETIDO"),
            ]
        )
    assert str(error.value) == MENSAJE_DUPLICADO.format(codigo="MAT-REPETIDO")


@pytest.mark.parametrize("cantidad", [True, False, "10", None, [1]])
def test_registrar_compra_rechaza_cantidad_de_tipo_invalido(
    catalogo_sintetico, cantidad
) -> None:
    with pytest.raises(ErrorInventario) as error:
        catalogo_sintetico.registrar_compra("MAT-CERA", cantidad)
    assert str(error.value) == MENSAJE_CANTIDAD
    assert catalogo_sintetico.existencia("MAT-CERA") == pytest.approx(800)


@pytest.mark.parametrize(
    "cantidad", [float("nan"), float("inf"), float("-inf")]
)
def test_registrar_compra_rechaza_cantidad_no_finita(
    catalogo_sintetico, cantidad
) -> None:
    with pytest.raises(ErrorInventario) as error:
        catalogo_sintetico.registrar_compra("MAT-CERA", cantidad)
    assert str(error.value) == MENSAJE_CANTIDAD
    assert catalogo_sintetico.historial() == []


@pytest.mark.parametrize("fecha", ["2026-11-25", 20261125, True])
def test_registrar_compra_rechaza_fecha_invalida(
    catalogo_sintetico, fecha
) -> None:
    with pytest.raises(ErrorInventario) as error:
        catalogo_sintetico.registrar_compra("MAT-CERA", 100, fecha=fecha)
    assert str(error.value) == MENSAJE_FECHA
    assert catalogo_sintetico.existencia("MAT-CERA") == pytest.approx(800)


@pytest.mark.parametrize("codigo", [None, 123, "", "X" * 51])
def test_registrar_compra_rechaza_codigo_invalido(
    catalogo_sintetico, codigo
) -> None:
    with pytest.raises(ErrorInventario) as error:
        catalogo_sintetico.registrar_compra(codigo, 100)
    assert str(error.value) == MENSAJE_MATERIAL.format(codigo=codigo)
    assert catalogo_sintetico.historial() == []


@pytest.mark.parametrize(
    "cantidad, fecha",
    [(0, None), ("10", None), (100, "2026-11-25")],
)
def test_registrar_compra_no_cambia_estado_si_falla(
    catalogo_sintetico, cantidad, fecha
) -> None:
    with pytest.raises(ErrorInventario):
        catalogo_sintetico.registrar_compra("MAT-CERA", cantidad, fecha=fecha)
    assert catalogo_sintetico.existencia("MAT-CERA") == pytest.approx(800)
    assert catalogo_sintetico.historial() == []


@pytest.mark.parametrize("cantidad", [True, "5", None, [1]])
def test_consumir_material_rechaza_cantidad_de_tipo_invalido(
    catalogo_sintetico, cantidad
) -> None:
    with pytest.raises(ErrorInventario) as error:
        catalogo_sintetico.consumir_material("MAT-CERA", cantidad)
    assert str(error.value) == MENSAJE_CANTIDAD
    assert catalogo_sintetico.existencia("MAT-CERA") == pytest.approx(800)


@pytest.mark.parametrize("cantidad", [float("nan"), float("inf")])
def test_consumir_material_rechaza_cantidad_no_finita(
    catalogo_sintetico, cantidad
) -> None:
    with pytest.raises(ErrorInventario) as error:
        catalogo_sintetico.consumir_material("MAT-CERA", cantidad)
    assert str(error.value) == MENSAJE_CANTIDAD
    assert catalogo_sintetico.existencia("MAT-CERA") == pytest.approx(800)


@pytest.mark.parametrize("codigo", [None, 123, "", "X" * 51])
def test_consumir_material_rechaza_codigo_invalido(
    catalogo_sintetico, codigo
) -> None:
    with pytest.raises(ErrorInventario) as error:
        catalogo_sintetico.consumir_material(codigo, 1)
    assert str(error.value) == MENSAJE_MATERIAL.format(codigo=codigo)


@pytest.mark.parametrize("codigo", ["MAT-NOEXISTE", "", "X" * 51])
def test_historial_de_codigo_inexistente_devuelve_lista_vacia(
    catalogo_sintetico, codigo
) -> None:
    assert catalogo_sintetico.historial(codigo) == []


@pytest.mark.parametrize("codigo", [None, 123, ""])
def test_existencia_rechaza_codigo_invalido(catalogo_sintetico, codigo) -> None:
    with pytest.raises(ErrorInventario) as error:
        catalogo_sintetico.existencia(codigo)
    assert str(error.value) == MENSAJE_MATERIAL.format(codigo=codigo)


def test_materiales_bajo_minimo_devuelve_copias(catalogo_sintetico) -> None:
    bajos = catalogo_sintetico.materiales_bajo_minimo()
    frasco = next(m for m in bajos if m.codigo == "MAT-FRASCO")
    frasco.existencia = 9999
    assert catalogo_sintetico.existencia("MAT-FRASCO") == pytest.approx(10)
