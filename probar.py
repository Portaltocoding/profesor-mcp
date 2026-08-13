"""Cliente de prueba para el servidor profesor.

QUE HACE : arranca el servidor como subproceso, hace el handshake, y llama a la tool.
COMO     : usa el cliente stdio del propio SDK. Es exactamente lo que hace Claude Code.
POR QUE  : probar a mano con echo/pipe funciona a medias: si stdin se cierra antes de
           que el servidor responda, pierdes la respuesta. El cliente real espera bien.
USO      : uv run python probar.py
"""

import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# QUE HACE : describe COMO lanzar el servidor.
# COMO     : command + args es literalmente lo que se ejecuta en una terminal.
# FALLA SI : el comando no esta en el PATH del proceso -> "No such file or directory".
PARAMS = StdioServerParameters(
    command="uv",
    args=["run", "profesor-mcp"],
)


async def main() -> None:
    # QUE HACE : abre los dos tubos (lectura/escritura) contra el subproceso.
    # COMO     : 'async with' garantiza que el subproceso se mata al salir.
    async with stdio_client(PARAMS) as (leer, escribir):
        # QUE HACE : envuelve los tubos en una sesion que habla JSON-RPC.
        async with ClientSession(leer, escribir) as sesion:
            # PASO 1 - handshake. Obligatorio y primero.
            # FALLA SI : llamas a cualquier otro metodo antes -> el servidor lo rechaza.
            # NOTA: el SDK v2 expone los campos en snake_case (server_info).
            #       El JSON del protocolo por debajo los manda en camelCase
            #       (serverInfo). Si copias codigo viejo con camelCase -> AttributeError.
            info = await sesion.initialize()
            print("handshake OK ->", info.server_info.name, info.server_info.version)

            # PASO 2 - descubrimiento. Que sabe hacer este servidor.
            tools = await sesion.list_tools()
            print("tools       ->", [t.name for t in tools.tools])

            prompts = await sesion.list_prompts()
            print("prompts     ->", [p.name for p in prompts.prompts])

            # PASO 3 - ejecucion. Aqui es donde el servidor hace su trabajo.
            # COMO : 'arguments' debe encajar con el input_schema de la tool.
            resultado = await sesion.call_tool(
                "explicar",
                arguments={"tema": "los closures en JavaScript", "nivel": "novato"},
            )
            texto = resultado.content[0].text
            print()
            print("=== LO QUE RECIBE CLAUDE ===")
            print(texto)


if __name__ == "__main__":
    asyncio.run(main())
