"""Paquete profesor_mcp.

QUE HACE : reexporta 'main' para que el comando 'profesor-mcp' lo encuentre.
COMO     : el pyproject.toml declara profesor-mcp = "profesor_mcp:main".
           Eso significa: "en el paquete profesor_mcp, busca el atributo main".
           Sin esta linea, main vive en server.py y el paquete no lo expone.
FALLA SI : borras este import -> el comando falla con AttributeError: main.
"""

from profesor_mcp.server import main

# QUE HACE : declara la API publica del paquete.
# COMO     : 'from profesor_mcp import *' solo traera lo que este en esta lista.
# NOTA     : es higiene, no obligatorio. Documenta la intencion.
__all__ = ["main"]
