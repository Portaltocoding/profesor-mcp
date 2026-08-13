"""Servidor MCP cocina. Generado desde 01-escribe-tu-propio-mcp.ipynb."""

import sys
from typing import Literal

from mcp.server.mcpserver import MCPServer

cocina = MCPServer(
    name="cocina",
    title="Ayudante de cocina",
    version="0.1.0",
    instructions="Utilidades de cocina: conversiones y reescalado de recetas.",
)


def log(mensaje: str) -> None:
    """Depuracion. SIEMPRE a stderr: stdout es el canal del protocolo."""
    print(mensaje, file=sys.stderr, flush=True)


@cocina.tool(name="convertir")
def convertir(
    cantidad: float,
    origen: Literal["g", "kg", "oz", "lb"],
    destino: Literal["g", "kg", "oz", "lb"],
) -> str:
    """Convierte una cantidad entre unidades de peso.

    Úsala cuando aparezcan unidades de peso mezcladas en una receta.
    No la uses para volumen (ml, tazas) ni para temperatura.

    Args:
        cantidad: El número a convertir.
        origen: Unidad de partida.
        destino: Unidad de llegada.
    """
    log(f"convertir({cantidad}, {origen}, {destino})")
    a_gramos = {"g": 1.0, "kg": 1000.0, "oz": 28.3495, "lb": 453.592}
    resultado = cantidad * a_gramos[origen] / a_gramos[destino]
    return f"{cantidad} {origen} = {resultado:.2f} {destino}"


@cocina.tool(name="dividir_receta")
def dividir_receta(comensales_original: int, comensales_nuevo: int) -> str:
    """Calcula el factor para reescalar una receta a otro número de comensales.

    Úsala cuando quieran adaptar una receta a más o menos gente.

    Args:
        comensales_original: Para cuántos es la receta actualmente.
        comensales_nuevo: Para cuántos la quieren.
    """
    if comensales_original <= 0:
        raise ValueError(
            f"comensales_original debe ser > 0. Recibido: {comensales_original}."
        )
    if comensales_nuevo <= 0:
        raise ValueError(f"comensales_nuevo debe ser > 0. Recibido: {comensales_nuevo}.")
    return f"Multiplica cada ingrediente por {comensales_nuevo / comensales_original:.2f}"


# ---- BLOQUE DE ARRANQUE. Sin esto el archivo no es un servidor, solo codigo.
def main() -> None:
    log("[cocina] arrancando en stdio")
    cocina.run(transport="stdio")


if __name__ == "__main__":
    main()
