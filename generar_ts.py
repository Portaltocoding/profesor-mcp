"""QUE HACE : traduce los textos de server.py a TypeScript.

POR QUE EXISTE
    El servidor vive dos veces: en Python (PyPI) y en TypeScript (npm). Los
    moldes son 385 lineas de prosa castellana y son el valor del proyecto. Si
    vivieran en los dos sitios a la vez, tocarias una ley del MOLDE_MANUAL en
    Python, se te olvidaria en TS, y a los tres meses los dos servidores
    explicarian distinto sin que nadie lo notara.

    Aqui no hay dos copias: hay una fuente y una derivacion. Python manda.

COMO
    Importa server.py y lee sus constantes ya evaluadas. No parsea texto ni
    usa expresiones regulares: si el fichero importa, los datos son correctos
    por construccion.

USO
    uv run python generar_ts.py

FALLA SI : editas ts/src/moldes.ts a mano. La proxima regeneracion te lo pisa.
"""

from __future__ import annotations

import sys
from pathlib import Path

from profesor_mcp import server as fuente

DESTINO = Path(__file__).parent / "ts" / "src" / "moldes.ts"


def a_literal(texto: str) -> str:
    """QUE HACE : convierte un string de Python en un template literal de JS.

    COMO     : escapa las tres secuencias que en JS significan algo dentro de
               las comillas invertidas. El orden importa: la barra invertida va
               PRIMERA, o volveria a escapar las barras que metemos despues.
    OJO      : `backtick` aparece de verdad en MARCADO. Sin este escape, el
               fichero generado no compilaria.
    """
    escapado = texto.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
    return f"`{escapado}`"


def bloque_diccionario(nombre: str, datos: dict[str, str]) -> str:
    """QUE HACE : escribe un diccionario de Python como objeto de TypeScript."""
    lineas = [f"export const {nombre}: Record<string, string> = {{"]
    for clave, valor in datos.items():
        # Las claves van entre comillas SIEMPRE: 'out of the box' lleva espacios
        # y sin comillas no seria un identificador valido.
        lineas.append(f"  {clave!r}: {a_literal(valor)},".replace("'", '"', 2))
    lineas.append("};")
    return "\n".join(lineas)


def main() -> int:
    if not DESTINO.parent.exists():
        print(f"error: no existe {DESTINO.parent}", file=sys.stderr)
        return 1

    partes = [
        "// ╔══════════════════════════════════════════════════════════════════╗",
        "// ║  FICHERO GENERADO — no lo edites a mano.                         ║",
        "// ║                                                                  ║",
        "// ║  Fuente de verdad : src/profesor_mcp/server.py (ZONAS 3 y 4)     ║",
        "// ║  Regenerar        : uv run python generar_ts.py                  ║",
        "// ║                                                                  ║",
        "// ║  Si cambias un molde aqui, la proxima regeneracion te lo pisa    ║",
        "// ║  y las dos versiones del servidor volveran a explicar igual.     ║",
        "// ╚══════════════════════════════════════════════════════════════════╝",
        "",
    ]

    # Los moldes, uno por constante, con el mismo nombre que en Python.
    for nombre in ("CLASICO", "CORNELL", "FEYNMAN", "MANUAL", "LIBRE"):
        molde = getattr(fuente, f"MOLDE_{nombre}")
        partes.append(f"export const MOLDE_{nombre} = {a_literal(molde)};")
        partes.append("")

    # El selector. Se reconstruye por nombre en vez de copiar los textos otra
    # vez: asi MODOS y los moldes no pueden separarse.
    partes.append("export const MODOS: Record<string, string> = {")
    for clave in fuente.MODOS:
        partes.append(f'  "{clave}": MOLDE_{clave.upper()},')
    partes.append("};")
    partes.append("")

    # Los ejes.
    for nombre, datos in (
        ("NIVELES", fuente.NIVELES),
        ("TONO", fuente.TONO),
        ("EXTENSION", fuente.EXTENSION),
    ):
        partes.append(bloque_diccionario(nombre, datos))
        partes.append("")

    partes.append(f"export const MARCADO = {a_literal(fuente.MARCADO)};")
    partes.append("")

    DESTINO.write_text("\n".join(partes), encoding="utf-8")
    print(f"generado: {DESTINO.relative_to(Path.cwd())} ({len(partes)} bloques)")
    print(f"  moldes: {len(fuente.MODOS)}  niveles: {len(fuente.NIVELES)}  "
          f"tonos: {len(fuente.TONO)}  extensiones: {len(fuente.EXTENSION)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
