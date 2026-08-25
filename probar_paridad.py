"""QUE HACE : comprueba que el servidor de Python y el de TypeScript devuelven
              exactamente el mismo texto.

POR QUE EXISTE
    'Se genera desde el Python' es una promesa. Esto la verifica. Si alguien
    toca la mecanica de un lado y se olvida del otro, o si el generador escapa
    mal un caracter, aqui salta y no en la cara de quien instale el paquete.

COMO
    Lanza los dos servidores como subprocesos, habla JSON-RPC 2.0 por stdin y
    stdout igual que haria un cliente de verdad, y compara los textos byte a
    byte para toda la matriz de combinaciones.

    Usa el PROMPT y no la TOOL a proposito: el prompt acepta los ejes como
    argumentos, asi que se pueden recorrer todos sin simular un dialogo.

USO
    uv run python probar_paridad.py     (requiere: cd ts && npm run build)
"""

from __future__ import annotations

import json
import subprocess
import sys
from itertools import product
from pathlib import Path

RAIZ = Path(__file__).parent
PROTOCOLO = "2025-06-18"

MODOS = ["clasico", "cornell", "feynman", "manual", "libre"]
NIVELES = ["novato", "intermedio", "avanzado"]
TONOS = ["formal", "out of the box"]
EXTENSIONES = ["normal", "corto"]


class Servidor:
    """Un servidor MCP hablado por stdio, como lo haria un cliente."""

    def __init__(self, nombre: str, comando: list[str]) -> None:
        self.nombre = nombre
        self.proc = subprocess.Popen(
            comando,
            cwd=RAIZ,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,  # el log() de los servidores va aqui
            text=True,
            encoding="utf-8",
            bufsize=1,
        )
        self.id = 0

    def pedir(self, metodo: str, params: dict) -> dict:
        self.id += 1
        mensaje = {"jsonrpc": "2.0", "id": self.id, "method": metodo, "params": params}
        assert self.proc.stdin and self.proc.stdout
        self.proc.stdin.write(json.dumps(mensaje) + "\n")
        self.proc.stdin.flush()
        while True:
            linea = self.proc.stdout.readline()
            if not linea:
                raise RuntimeError(f"{self.nombre}: el servidor cerro la salida")
            respuesta = json.loads(linea)
            # Las notificaciones no llevan 'id'. Solo nos interesa la respuesta.
            if respuesta.get("id") == self.id:
                if "error" in respuesta:
                    raise RuntimeError(f"{self.nombre}: {respuesta['error']}")
                return respuesta["result"]

    def notificar(self, metodo: str) -> None:
        assert self.proc.stdin
        self.proc.stdin.write(json.dumps({"jsonrpc": "2.0", "method": metodo}) + "\n")
        self.proc.stdin.flush()

    def arrancar(self) -> dict:
        info = self.pedir("initialize", {
            "protocolVersion": PROTOCOLO,
            "capabilities": {},
            "clientInfo": {"name": "probar-paridad", "version": "0.1.0"},
        })
        self.notificar("notifications/initialized")
        return info

    def explicacion(self, tema: str, **ejes: str) -> str:
        res = self.pedir("prompts/get", {
            "name": "profesor",
            "arguments": {"tema": tema, **ejes},
        })
        return res["messages"][0]["content"]["text"]

    def cerrar(self) -> None:
        self.proc.terminate()
        self.proc.wait(timeout=5)


def main() -> int:
    py = Servidor("python", ["uv", "run", "profesor-mcp"])
    ts = Servidor("typescript", ["node", "ts/dist/server.js"])

    try:
        info_py = py.arrancar()
        info_ts = ts.arrancar()

        print("=== identidad ===")
        for etiqueta, info in (("python", info_py), ("typescript", info_ts)):
            si = info["serverInfo"]
            print(f"  {etiqueta:11} {si['name']} v{si['version']}  "
                  f"protocolo={info['protocolVersion']}")

        # Que las dos declaren las mismas capacidades importa: un cliente
        # decide que puede pedir mirando esto.
        if info_py["capabilities"].keys() != info_ts["capabilities"].keys():
            print(f"  AVISO capacidades distintas: "
                  f"{sorted(info_py['capabilities'])} vs "
                  f"{sorted(info_ts['capabilities'])}")

        print("\n=== paridad de textos ===")
        tema = "la recursión y por qué el caso base no es opcional"
        fallos = 0
        casos = 0
        for modo, nivel, tono, ext in product(MODOS, NIVELES, TONOS, EXTENSIONES):
            casos += 1
            ejes = {"modo": modo, "nivel": nivel, "tono": tono, "extension": ext}
            a = py.explicacion(tema, **ejes)
            b = ts.explicacion(tema, **ejes)
            if a != b:
                fallos += 1
                print(f"  DIFIERE  {ejes}")
                print(f"    python     {len(a)} chars")
                print(f"    typescript {len(b)} chars")
                for i, (ca, cb) in enumerate(zip(a, b)):
                    if ca != cb:
                        print(f"    primer byte distinto en {i}: "
                              f"{ca!r} vs {cb!r}")
                        print(f"    contexto py: ...{a[max(0,i-60):i+60]!r}")
                        print(f"    contexto ts: ...{b[max(0,i-60):i+60]!r}")
                        break

        # Un caso mas: el tema entra tal cual, con acentos y comillas raras.
        casos += 1
        raro = 'un tema con `backticks`, "comillas", {llaves} y ñ'
        if py.explicacion(raro) != ts.explicacion(raro):
            fallos += 1
            print("  DIFIERE  el tema con caracteres especiales")

        print(f"\n  {casos - fallos}/{casos} casos identicos")
        if fallos:
            print("\nFALLO: las dos versiones no explican igual.")
            return 1
        print("\nOK: las dos versiones devuelven el mismo texto.")
        return 0
    finally:
        py.cerrar()
        ts.cerrar()


if __name__ == "__main__":
    raise SystemExit(main())
