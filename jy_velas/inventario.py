"""Inventario de JY Velas y Jabones: registro de compras de materiales (HU-01)."""

from __future__ import annotations

import math
from dataclasses import dataclass, replace
from datetime import date
from typing import Iterable

MENSAJE_CANTIDAD_INVALIDA = "La cantidad debe ser mayor que cero"
MENSAJE_MATERIAL_NO_REGISTRADO = "El material '{codigo}' no está registrado"
MENSAJE_MATERIAL_DUPLICADO = "El material '{codigo}' está duplicado en el catálogo"
MENSAJE_CODIGO_INVALIDO = "El código del material debe ser una cadena no vacía"
MENSAJE_FECHA_INVALIDA = "La fecha de la compra debe ser una fecha válida"
MENSAJE_VALOR_INVALIDO = (
    "La existencia y el mínimo deben ser números finitos no negativos"
)
MENSAJE_LONGITUD_INVALIDA = (
    "El código, el nombre o la unidad superan la longitud permitida"
)
MENSAJE_STOCK_INSUFICIENTE = (
    "No hay existencia suficiente de '{codigo}': "
    "disponible {disponible:g}, solicitado {cantidad:g}"
)


class ErrorInventario(Exception):
    """Error de negocio del inventario."""


@dataclass
class Material:
    """Material del catálogo con su existencia y su mínimo de aviso."""

    codigo: str
    nombre: str
    unidad: str
    existencia: float = 0.0
    minimo: float = 0.0

    def __post_init__(self) -> None:
        if not isinstance(self.codigo, str) or not self.codigo:
            raise ErrorInventario(MENSAJE_CODIGO_INVALIDO)
        if not isinstance(self.nombre, str) or not isinstance(self.unidad, str):
            raise ErrorInventario(MENSAJE_CODIGO_INVALIDO)
        if len(self.codigo) > 50 or len(self.nombre) > 100 or len(self.unidad) > 20:
            raise ErrorInventario(MENSAJE_LONGITUD_INVALIDA)
        for valor in (self.existencia, self.minimo):
            if (
                isinstance(valor, bool)
                or not isinstance(valor, (int, float))
                or not math.isfinite(valor)
                or valor < 0
            ):
                raise ErrorInventario(MENSAJE_VALOR_INVALIDO)


@dataclass(frozen=True)
class Compra:
    """Registro inmutable de una compra de material."""

    codigo_material: str
    cantidad: float
    fecha: date


class Inventario:
    """Catálogo de materiales y su historial de compras."""

    def __init__(self, materiales: Iterable[Material] = ()) -> None:
        self._materiales: dict[str, Material] = {}
        for material in materiales:
            if material.codigo in self._materiales:
                raise ErrorInventario(
                    MENSAJE_MATERIAL_DUPLICADO.format(codigo=material.codigo)
                )
            self._materiales[material.codigo] = material
        self._compras: list[Compra] = []

    def registrar_compra(
        self,
        codigo: str,
        cantidad: float,
        fecha: date | None = None,
    ) -> Compra:
        """Registra una compra y suma la cantidad a la existencia.

        Args:
            codigo: Código de un material ya registrado en el catálogo.
            cantidad: Número finito estrictamente mayor que cero, en la unidad
                del material.
            fecha: Fecha de la compra. Si es ``None``, se usa ``date.today()``.

        Returns:
            La compra registrada como un objeto inmutable ``Compra``.

        Raises:
            ErrorInventario: Si el material no existe, la cantidad no es un
                número finito positivo o la fecha no es ``None`` ni ``date``.
        """
        material = self._buscar_material(codigo)
        self._validar_cantidad(cantidad)
        self._validar_fecha(fecha)
        material.existencia += cantidad
        compra = Compra(
            codigo_material=codigo,
            cantidad=cantidad,
            fecha=fecha or date.today(),
        )
        self._compras.append(compra)
        return compra

    def existencia(self, codigo: str) -> float:
        """Devuelve la existencia actual de un material.

        Args:
            codigo: Código del material registrado en el catálogo.

        Returns:
            La existencia como ``float``, en la unidad del material.

        Raises:
            ErrorInventario: Si el código no es una cadena válida o el material
                no está registrado.
        """
        return self._buscar_material(codigo).existencia

    def historial(self, codigo: str | None = None) -> list[Compra]:
        """Devuelve las compras registradas, opcionalmente filtradas por material.

        Si el código no existe en el catálogo, devuelve una lista vacía: el filtro
        es una consulta y no una operación de negocio (ambigüedad documentada).

        Args:
            codigo: Filtro opcional por código de material. Sin valor, devuelve
                todas las compras.

        Returns:
            Lista de compras en el orden en que se registraron.
        """
        if codigo is None:
            return list(self._compras)
        return [compra for compra in self._compras if compra.codigo_material == codigo]

    def consumir_material(self, codigo: str, cantidad: float) -> float:
        """Descuenta la cantidad consumida y devuelve la existencia restante.

        Reglas: el material debe existir, la cantidad debe ser un número finito
        estrictamente positivo y no puede superar la existencia disponible.

        Args:
            codigo: Código del material registrado en el catálogo.
            cantidad: Cantidad a descontar, finita y mayor que cero.

        Returns:
            La existencia restante después del consumo.

        Raises:
            ErrorInventario: Si el material no existe, la cantidad es inválida
                o supera la existencia disponible.
        """
        material = self._buscar_material(codigo)
        self._validar_cantidad(cantidad)
        if cantidad > material.existencia:
            raise ErrorInventario(
                MENSAJE_STOCK_INSUFICIENTE.format(
                    codigo=codigo,
                    disponible=float(material.existencia),
                    cantidad=float(cantidad),
                )
            )
        material.existencia -= cantidad
        return material.existencia

    def materiales_bajo_minimo(self) -> list[Material]:
        """Devuelve los materiales cuya existencia es igual o menor que su mínimo.

        Un mínimo de cero solo genera alerta cuando la existencia también es cero.

        Returns:
            Copias de los materiales en alerta, en el orden del catálogo. Modificar
            una copia no cambia el estado interno del inventario.
        """
        return [
            replace(material)
            for material in self._materiales.values()
            if material.existencia <= material.minimo
        ]

    def _buscar_material(self, codigo: str) -> Material:
        """Busca un material del catálogo o lanza un error de negocio."""
        if not isinstance(codigo, str) or not codigo or len(codigo) > 50:
            raise ErrorInventario(
                MENSAJE_MATERIAL_NO_REGISTRADO.format(codigo=codigo)
            )
        try:
            return self._materiales[codigo]
        except KeyError as error:
            raise ErrorInventario(
                MENSAJE_MATERIAL_NO_REGISTRADO.format(codigo=codigo)
            ) from error

    @staticmethod
    def _validar_cantidad(cantidad: float) -> None:
        """Rechaza cantidades que no sean números finitos estrictamente positivos."""
        if (
            isinstance(cantidad, bool)
            or not isinstance(cantidad, (int, float))
            or not math.isfinite(cantidad)
            or cantidad <= 0
        ):
            raise ErrorInventario(MENSAJE_CANTIDAD_INVALIDA)

    @staticmethod
    def _validar_fecha(fecha: date | None) -> None:
        """Rechaza fechas que no sean None o una instancia de date."""
        if fecha is not None and not isinstance(fecha, date):
            raise ErrorInventario(MENSAJE_FECHA_INVALIDA)
