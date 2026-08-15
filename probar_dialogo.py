"""Cliente de prueba para el dialogo (elicitation).

QUE HACE : arranca el servidor y RESPONDE automaticamente a los dialogos.
POR QUE  : ctx.elicit() se queda ESPERANDO. Un cliente que no sabe responder
           deja la tool colgada para siempre. Por eso hasta ahora probar era
           trivial y a partir de ahora no lo es.
COMO     : ClientSession acepta 'elicitation_callback'. Es una funcion que
           el SDK llama cuando el servidor pregunta. Aqui simulamos al humano.
USO      : uv run python probar_dialogo.py
"""

import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import ElicitRequestFormParams, ElicitResult

PARAMS = StdioServerParameters(command="uv", args=["run", "profesor-mcp"])


def responder_como(respuestas: list):
    """Fabrica un callback que va contestando de la lista, en orden.

    Cada elemento puede ser:
      dict  -> el humano ACEPTA y elige esos valores
      "cancel" / "decline" -> el humano cierra el dialogo
    """
    pendientes = list(respuestas)

    async def callback(context, params: ElicitRequestFormParams) -> ElicitResult:
        siguiente = pendientes.pop(0) if pendientes else "cancel"
        # OJO: requested_schema en snake_case. El JSON del protocolo lo manda
        # como 'requestedSchema' (camelCase), pero el SDK v2 lo expone en
        # snake_case. Es la misma trampa de server_info / input_schema.
        opciones = list((params.requested_schema or {}).get("properties", {}).keys())
        print(f'    [dialogo] "{params.message}"')
        print(f"    [dialogo]  campos: {opciones}  ->  respondo: {siguiente}")
        if isinstance(siguiente, dict):
            return ElicitResult(action="accept", content=siguiente)
        return ElicitResult(action=siguiente)

    return callback


async def caso(titulo: str, respuestas: list) -> None:
    """Ejecuta la tool una vez, con un guion de respuestas concreto."""
    print(f"\n=== {titulo} ===")
    async with stdio_client(PARAMS) as (leer, escribir):
        async with ClientSession(
            leer, escribir, elicitation_callback=responder_como(respuestas)
        ) as sesion:
            await sesion.initialize()
            r = await sesion.call_tool("explicar", {"tema": "los closures"})
            texto = r.content[0].text
            # identificamos que molde salio por su primera marca distintiva
            if "sin saltarte pasos" in texto:
                molde = "CLASICO"
            elif "**NOTAS**" in texto:
                molde = "CORNELL"
            elif "EXPLICACIÓN LLANA" in texto:
                molde = "FEYNMAN"
            elif "**1. CONTRATO**" in texto:
                molde = "MANUAL"
            elif "sin andamiaje" in texto:
                molde = "LIBRE"
            else:
                molde = "???"
            nivel = next((n for n in ("NOVATO", "INTERMEDIO", "AVANZADO") if f"Nivel {n}" in texto), "-")
            tono = "OUT OF THE BOX" if "Tono OUT OF THE BOX" in texto else ("FORMAL" if "Tono FORMAL" in texto else "-")
            print(f"    RESULTADO -> molde={molde}  nivel={nivel}  tono={tono}")


async def main() -> None:
    # 1. Elige clasico -> DEBE preguntar dos veces (cascada)
    await caso(
        "clasico + ajustes",
        [{"modo": "clasico"}, {"nivel": "avanzado", "tono": "out of the box"}],
    )

    # 2. Elige cornell -> NO debe preguntar el segundo dialogo
    await caso("cornell (cerrado, sin cascada)", [{"modo": "cornell"}])

    # 3. Elige feynman -> igual
    await caso("feynman (cerrado, sin cascada)", [{"modo": "feynman"}])

    # 4. Cancela el primero -> clasico + intermedio + formal
    await caso("cancela el paso 1", ["cancel"])

    # 5. Elige clasico y cancela el segundo -> clasico + defaults
    await caso("clasico, cancela el paso 2", [{"modo": "clasico"}, "cancel"])

    # 6. Elige manual -> cascada propia. Mira los CAMPOS del segundo dialogo:
    #    tiene que salir ['nivel'] a secas. Si ahi apareciera 'tono', estariamos
    #    preguntando algo que el molde tira, que es justo lo que no queremos.
    await caso("manual + nivel", [{"modo": "manual"}, {"nivel": "novato"}])

    # 7. Elige manual y cancela el paso 2 -> manual con nivel por defecto
    await caso("manual, cancela el paso 2", [{"modo": "manual"}, "cancel"])

    # 8. Elige libre -> sin cascada, como los cerrados
    await caso("libre (sin cascada)", [{"modo": "libre"}])


if __name__ == "__main__":
    asyncio.run(main())
