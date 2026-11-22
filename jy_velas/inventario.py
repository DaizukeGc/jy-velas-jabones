"""Inventario de JY Velas y Jabones: registro de compras de materiales (HU-01)."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date
from typing import Iterable

MENSAJE_CANTIDAD_INVALIDA = "La cantidad debe ser mayor que cero"
MENSAJE_MATERIAL_NO_REGISTRADO = "El material '{codigo}' no está registrado"
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


@dataclass(frozen=True)
class Compra:
    """Registro inmutable de una compra de material."""

    codigo_material: str
    cantidad: float
    fecha: date


class Inventario:
    """Catálogo de materiales y su historial de compras."""

    def __init__(self, materiales: Iterable[Material] = ()) -> None:
        self._materiales = {material.codigo: material for material in materiales}
        self._compras: list[Compra] = []

    def registrar_compra(self, codigo: str, cantidad: float, fecha: date | None = None) -> Compra:
        """Suma la cantidad comprada a la existencia del material y registra la compra."""
        material = self._buscar_material(codigo)
        self._validar_cantidad(cantidad)
        material.existencia += cantidad
        compra = Compra(codigo_material=codigo, cantidad=cantidad, fecha=fecha or date.today())
        self._compras.append(compra)
        return compra

    def existencia(self, codigo: str) -> float:
        """Devuelve la existencia actual de un material."""
        return self._buscar_material(codigo).existencia

    def historial(self, codigo: str | None = None) -> list[Compra]:
        """Devuelve las compras registradas, opcionalmente filtradas por material.

        Si el código no existe en el catálogo, devuelve una lista vacía: el filtro
        es una consulta y no una operación de negocio (ambigüedad documentada).
        """
        if codigo is None:
            return list(self._compras)
        return [compra for compra in self._compras if compra.codigo_material == codigo]

    def consumir_material(self, codigo: str, cantidad: float) -> float:
        """Descuenta la cantidad consumida y devuelve la existencia restante.

        Reglas: el material debe existir, la cantidad debe ser un número finito
        estrictamente positivo y no puede superar la existencia disponible.
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
        """
        return [
            material
            for material in self._materiales.values()
            if material.existencia <= material.minimo
        ]

    def _buscar_material(self, codigo: str) -> Material:
        """Busca un material del catálogo o lanza un error de negocio."""
        try:
            return self._materiales[codigo]
        except KeyError as error:
            raise ErrorInventario(MENSAJE_MATERIAL_NO_REGISTRADO.format(codigo=codigo)) from error

    @staticmethod
    def _validar_cantidad(cantidad: float) -> None:
        """Rechaza cantidades que no sean números finitos estrictamente positivos."""
        if not math.isfinite(cantidad) or cantidad <= 0:
            raise ErrorInventario(MENSAJE_CANTIDAD_INVALIDA)
