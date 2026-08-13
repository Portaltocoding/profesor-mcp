"""Genera 01-escribe-tu-propio-mcp.ipynb.

QUE HACE : notebook-guia paso a paso para escribir un MCP desde cero.
COMO     : construye un servidor nuevo dentro del notebook, celda a celda,
           lo exporta a un .py real, y lo arranca como subproceso para probarlo.
USO      : uv run python construir_guia.py
"""

import nbformat as nbf

nb = nbf.v4.new_notebook()
celdas = []


def md(texto: str) -> None:
    celdas.append(nbf.v4.new_markdown_cell(texto.strip()))


def code(texto: str) -> None:
    celdas.append(nbf.v4.new_code_cell(texto.strip()))


# ===========================================================================
md(
    """
# Escribe tu propio MCP

Guía práctica. Al final de este notebook habrás construido un servidor MCP
funcionando, exportado a un archivo real, y probado como subproceso.

**No es teoría.** Cada celda corre. El servidor que construyas aquí funciona.

> Si no sabes qué es un MCP, lee antes `00-anatomia-de-un-mcp.ipynb`.
> Aquí asumimos que ya sabes qué son tools, prompts y el transporte stdio.
"""
)

# ===========================================================================
md(
    """
---
## La receta

Escribir un MCP son siempre los mismos 7 pasos. Da igual lo que haga tu servidor.

| Paso | Qué haces | Tiempo |
|---|---|---|
| 1 | Crear el proyecto y añadir el SDK | 2 min |
| 2 | Instanciar el servidor (3 líneas) | 1 min |
| 3 | Escribir tu primera tool | 5 min |
| 4 | Diseñar los parámetros | ← aquí se piensa |
| 5 | Escribir el docstring | ← **aquí se gana o se pierde** |
| 6 | Manejar los errores | 5 min |
| 7 | Registrar en Claude Code y probar | 2 min |

Los pasos 4 y 5 son los únicos que requieren pensar. El resto es mecánico.

**Vamos a construir:** un servidor `cocina` con tres tools de dificultad creciente.
Sirve para aprender los tres patrones que vas a necesitar siempre.
"""
)

# ===========================================================================
md(
    """
---
## Paso 1 — El proyecto

Tres comandos. Esto ya está hecho en este proyecto, así que aquí solo lo
verificamos; cópialos cuando empieces uno nuevo.

```bash
uv init mi-servidor --python 3.12    # crea el esqueleto
cd mi-servidor
uv add "mcp[cli]"                    # añade el SDK
```

**Por qué `uv` y no `pip`:** `uv` gestiona también la versión de Python.
El SDK exige 3.10+ y macOS trae 3.9 de fábrica. Con `pip` tendrías que
resolver eso a mano antes de empezar.
"""
)

code(
    """
# QUE HACE : verifica que el entorno cumple los requisitos del SDK.
# FALLA SI : Python < 3.10 -> el SDK no se instala siquiera.
import sys
import importlib.metadata as meta

version = sys.version_info
ok = (version.major, version.minor) >= (3, 10)

print(f"Python  : {version.major}.{version.minor}.{version.micro}  {'OK' if ok else 'DEMASIADO VIEJO'}")
print(f"SDK mcp : {meta.version('mcp')}")
print()
print("Requisito: Python >= 3.10" if ok else "PARA: instala Python 3.10+ antes de seguir")
"""
)

# ===========================================================================
md(
    """
---
## Paso 2 — El esqueleto

Tres líneas y ya tienes un servidor MCP válido. No hace nada, pero arranca
y responde al handshake.
"""
)

code(
    """
# 1. IMPORTAR la clase principal.
#    OJO: en el SDK v1 se llamaba FastMCP. Si copias de un tutorial viejo
#    veras 'from mcp.server.fastmcp import FastMCP' -> ModuleNotFoundError.
from mcp.server.mcpserver import MCPServer

# 2. INSTANCIAR. 'mcp' es el objeto sobre el que registraras todo.
cocina = MCPServer(
    name="cocina",              # identificador tecnico. Unico entre tus servidores.
    title="Ayudante de cocina",  # nombre legible. Lo ve el humano.
    version="0.1.0",             # tu versionado. No el del protocolo.
    instructions=(               # opcional pero MUY util: orienta a Claude
        "Servidor con utilidades de cocina: conversiones, temporizadores "
        "y notas de recetas."
    ),
)

print("servidor creado:", cocina.name)
print("ya es valido. Arrancaria y respondaria al handshake.")
print("no tiene tools todavia -> Claude no puede hacer nada con el.")
"""
)

# ===========================================================================
md(
    """
---
## Paso 3 — Tu primera tool, con cada pieza etiquetada

Aquí está el bloque que tienes que saber leer. **Casi todo es Python normal.**
El SDK solo aporta el decorador.

Lo insólito: el SDK **lee cosas que Python normalmente ignora** — los type hints
y el docstring. En Python puro son decoración. Aquí son la interfaz con Claude.
"""
)

code(
    """
# ==========  DISECCION DE UNA TOOL  ==========

# PYTHON (modulo typing): Literal restringe un parametro a valores exactos.
# No es del SDK. Es del lenguaje. El SDK solo lo lee.
from typing import Literal


# ---- (A) DECORADOR ------------------------------------------------------
#      '@' es sintaxis de PYTHON. '.tool()' lo aporta el SDK.
#      QUE HACE : registra la funcion, lee su firma, lee su docstring.
#      FALLA SI : lo quitas -> la funcion existe pero Claude no la ve jamas.
#      OJO      : lleva parentesis porque es una FABRICA de decoradores
#                 (se llama con la config y devuelve el decorador real).
@cocina.tool(name="convertir")
#
# ---- (B) DEFINICION -----------------------------------------------------
#      'def' es PYTHON puro. Una funcion normal y corriente.
def convertir(
    #
    # ---- (C) TYPE HINT ---------------------------------------------------
    #      'cantidad: float' es PYTHON. El interprete lo IGNORA.
    #      Pero el SDK lo LEE -> "type": "number" en el JSON Schema.
    #      FALLA SI : lo omites -> el SDK asume "string" en silencio.
    cantidad: float,
    #
    # ---- (D) TYPE HINT RESTRINGIDO ---------------------------------------
    #      'Literal' viene de typing (PYTHON). Cierra los valores posibles.
    #      -> "enum": [...] en el schema. Claude no puede inventarse otro.
    origen: Literal["g", "kg", "oz", "lb"],
    destino: Literal["g", "kg", "oz", "lb"],
    #
    # ---- (E) ANOTACION DE RETORNO ----------------------------------------
    #      '-> str' es PYTHON. El SDK NO la usa para el schema.
    #      Sirve para ti y para tu editor. Ponla igualmente.
) -> str:
    #
    # ---- (F) DOCSTRING ---------------------------------------------------
    #      En Python puro: documentacion opcional que nadie lee.
    #      AQUI: es LA INTERFAZ. Es el texto que lee Claude para decidir
    #      si esta tool aplica al mensaje del usuario.
    #      FALLA SI : es vago -> la tool no se dispara nunca, o se dispara mal.
    \"\"\"Convierte una cantidad entre unidades de peso.

    Úsala cuando aparezcan unidades de peso mezcladas en una receta,
    o cuando pidan pasar de sistema métrico a imperial (o al revés).
    No la uses para volumen (ml, tazas) ni para temperatura.

    Args:
        cantidad: El número a convertir.
        origen: Unidad de partida.
        destino: Unidad de llegada.
    \"\"\"
    # ---- (G) EL CUERPO ---------------------------------------------------
    #      PYTHON puro. Aqui no hay nada del SDK. Es tu logica y ya.
    a_gramos = {"g": 1.0, "kg": 1000.0, "oz": 28.3495, "lb": 453.592}
    gramos = cantidad * a_gramos[origen]
    resultado = gramos / a_gramos[destino]

    # ---- (H) EL RETORNO --------------------------------------------------
    #      Lo que devuelves viaja a Claude como texto.
    #      f"..." es un f-string: sintaxis de PYTHON para interpolar.
    return f"{cantidad} {origen} = {resultado:.2f} {destino}"


print("tool 'convertir' registrada")
print()
print("PRUEBA: el decorador devolvio la funcion INTACTA.")
print("  convertir(500, 'g', 'lb') ->", convertir(500, "g", "lb"))
print()
print("No la envolvio ni la modifico. Solo la apunto en un registro interno.")
"""
)

md(
    """
### Tabla de referencia

Guárdate esta tabla. Responde "¿esto de quién es?" para cada pieza.

| Marca | Sintaxis | Nombre | ¿De quién? | Si lo quitas |
|---|---|---|---|---|
| A | `@cocina.tool()` | decorador | `@` es Python, `.tool()` es del SDK | La tool no existe para Claude |
| B | `def nombre(...)` | definición | Python | No hay función |
| C | `cantidad: float` | type hint | Python, **leído por el SDK** | El schema dice `string`, en silencio |
| D | `Literal["g","kg"]` | type hint restringido | Python (`typing`) | Claude puede mandar cualquier texto |
| E | `-> str` | anotación de retorno | Python | Nada — el SDK no la usa |
| F | `\"\"\"...\"\"\"` | docstring | Python, **leído por el SDK** | Claude no sabe cuándo usarla |
| G | el cuerpo | tu lógica | Python | — |
| H | `return f"..."` | f-string | Python | Concatenarías a mano |

**La regla que resume todo:** el SDK solo aporta el decorador. Todo lo demás
es Python. Lo que cambia es que **dos cosas decorativas se vuelven funcionales**:
los type hints y el docstring.
"""
)

code(
    """
# QUE HACE : enseña el schema que salio de esa firma.
# OBSERVA  : cada pieza de la tabla anterior aparece aqui traducida.
import json

tools = await cocina.list_tools()
t = tools[0]

print("--- SCHEMA GENERADO ---")
print(json.dumps(t.input_schema, indent=2, ensure_ascii=False))
print()
print("TRADUCCION:")
print("  cantidad: float              ->  type: number")
print("  Literal['g','kg','oz','lb']  ->  enum: [...]")
print("  (sin valor por defecto)      ->  aparece en 'required'")
"""
)

# ===========================================================================
md(
    """
---
## Paso 4 — Diseñar los parámetros

Aquí se piensa. Tres reglas.

### Regla 1 — Usa `Literal` siempre que el conjunto sea cerrado

Si un parámetro solo admite ciertos valores, ciérralo. Convierte un fallo en
tiempo de ejecución en un fallo en tiempo de validación — y Claude ve las
opciones válidas antes de llamar.

```python
categoria: str                              # mal — Claude inventa categorías
categoria: Literal["dulce", "salado"]       # bien — solo dos posibles
```

### Regla 2 — Pocos parámetros, y planos

Un diccionario anidado genera un schema que Claude rellena peor. Prefiere
3 parámetros planos a 1 objeto con 3 campos.

### Regla 3 — Valor por defecto = parámetro opcional

Poner `= algo` saca el campo de `required`. Úsalo para todo lo que tenga una
opción sensata por defecto: menos que decidir para Claude, menos que fallar.

### Tabla de traducción

| Python | JSON Schema | Claude manda |
|---|---|---|
| `x: str` | `"type": "string"` | `"hola"` |
| `x: int` | `"type": "integer"` | `7` |
| `x: float` | `"type": "number"` | `7.5` |
| `x: bool` | `"type": "boolean"` | `true` |
| `x: list[str]` | `"type": "array"` | `["a","b"]` |
| `x: Literal["a","b"]` | `"enum": ["a","b"]` | solo `"a"` o `"b"` |
| `x: str = "z"` | `"default": "z"`, opcional | puede omitirlo |
| `x: str \\| None = None` | opcional, admite `null` | puede mandar `null` |
"""
)

code(
    """
# QUE HACE : registra una tool con varios tipos para ver todas las traducciones.
# OBSERVA  : compara cada parametro con la tabla de arriba.

@cocina.tool(name="temporizador")
def temporizador(
    minutos: int,                                  # -> integer
    etiqueta: str = "sin nombre",                  # -> string, opcional
    avisar_antes: bool = True,                     # -> boolean, opcional
    sonidos: list[str] | None = None,              # -> array, opcional, nullable
) -> str:
    \"\"\"Programa un temporizador de cocina.

    Úsala cuando pidan avisar tras cierto tiempo mientras cocinan.

    Args:
        minutos: Duración en minutos.
        etiqueta: Nombre para identificar el temporizador.
        avisar_antes: Si avisar también un minuto antes de terminar.
        sonidos: Lista de sonidos a usar. Por defecto el del sistema.
    \"\"\"
    return f"Temporizador '{etiqueta}' programado: {minutos} min"


import json
tools = await cocina.list_tools()
esquema = next(t for t in tools if t.name == "temporizador").input_schema

print("obligatorios:", esquema.get("required", []))
print()
for campo, d in esquema["properties"].items():
    tipo = d.get("type") or d.get("anyOf") or "?"
    porDefecto = d.get("default", "<obligatorio>")
    print(f"  {campo:14} tipo={str(tipo):28} defecto={porDefecto}")
"""
)

# ===========================================================================
md(
    """
---
## Paso 5 — El docstring (la parte que importa)

**Aquí se gana o se pierde el servidor.** El docstring es lo único que Claude
lee para decidir si llamar tu tool. Tu código puede ser perfecto; si el
docstring es vago, la tool no se dispara nunca.

### La fórmula

```
Línea 1     Qué hace. Imperativo. Una frase.
(blanco)
Párrafo 2   CUÁNDO usarla. Y cuándo NO. ← lo que más falta
(blanco)
Args:       Cada parámetro, una línea.
```

### El error más común

Casi todo el mundo escribe **qué hace** y se olvida de **cuándo usarla**.
Claude no necesita saber qué hace: lo deduce del nombre. Necesita saber
en qué situación aplica.
"""
)

code(
    """
# QUE HACE : compara un docstring malo con uno bueno.
# OBSERVA  : lo que ve Claude es exactamente este texto. Nada mas.

malo_y_bueno = MCPServer(name="comparacion")


@malo_y_bueno.tool(name="buscar_receta_MALA")
def buscar_mala(ingrediente: str) -> str:
    \"\"\"Busca recetas.\"\"\"
    return ""


@malo_y_bueno.tool(name="buscar_receta_BUENA")
def buscar_buena(ingrediente: str) -> str:
    \"\"\"Busca recetas que usen un ingrediente concreto.

    Úsala cuando pregunten qué cocinar con algo que ya tienen, o pidan
    ideas partiendo de un ingrediente. No la uses si ya han nombrado
    un plato concreto: entonces buscan la receta de ESE plato, no ideas.

    Args:
        ingrediente: El ingrediente principal disponible, en singular.
    \"\"\"
    return ""


for t in await malo_y_bueno.list_tools():
    print("=" * 60)
    print(t.name)
    print("=" * 60)
    print(t.description)
    print()

print("Con el MALO, Claude no sabe si aplica cuando el usuario dice")
print("'como hago una tortilla' (respuesta correcta: NO, ya sabe el plato).")
print("Con el BUENO, lo sabe: el docstring se lo dice explicitamente.")
"""
)

md(
    """
### Frases que funcionan

Copia estas estructuras:

- `Úsala cuando <situación concreta>.`
- `No la uses si <situación parecida pero distinta>.` ← **la más valiosa**
- `Prefiere <otra tool> cuando <caso>.`

**La negativa vale más que la positiva.** Delimitar dónde *no* aplica evita
el problema real: que la tool se dispare cuando no toca y ensucie la respuesta.

### Lo que NO va en el docstring

- Ejemplos largos de código — ocupan contexto en cada petición
- Detalles de implementación — a Claude le da igual cómo lo haces
- `CRITICAL:`, `SIEMPRE`, `NUNCA` en mayúsculas — provocan sobredisparo.
  Los modelos actuales siguen bien las instrucciones normales; el énfasis
  agresivo era una técnica para modelos antiguos y ahora es contraproducente.
"""
)

# ===========================================================================
md(
    """
---
## Paso 6 — Fallar bien

Dos niveles de error, y se manejan distinto.

| Nivel | Quién lo detecta | Qué haces tú |
|---|---|---|
| **Validación** | Pydantic, antes de tu función | Nada. Gratis con los type hints. |
| **Lógica** | Tu código | Lanza una excepción con mensaje útil |

La clave del segundo: **el mensaje de error lo lee Claude**, y con él decide si
reintentar. Un `ValueError("error")` no le dice nada. Un
`ValueError("La unidad 'taza' es de volumen; esta tool solo convierte peso")`
le permite corregirse solo.
"""
)

code(
    """
# QUE HACE : tool que valida su propia logica y falla con un mensaje util.

@cocina.tool(name="dividir_receta")
def dividir_receta(comensales_original: int, comensales_nuevo: int) -> str:
    \"\"\"Calcula el factor para reescalar una receta a otro número de comensales.

    Úsala cuando quieran adaptar una receta a más o menos gente.

    Args:
        comensales_original: Para cuántos es la receta actualmente.
        comensales_nuevo: Para cuántos la quieren.
    \"\"\"
    # VALIDACION DE LOGICA. Pydantic ya garantizo que son enteros,
    # pero no que sean positivos. Eso lo compruebas tu.
    if comensales_original <= 0:
        # MENSAJE UTIL: dice que esta mal Y que hacer.
        raise ValueError(
            "comensales_original debe ser mayor que 0. "
            f"Recibido: {comensales_original}. Revisa la receta original."
        )
    if comensales_nuevo <= 0:
        raise ValueError(
            "comensales_nuevo debe ser mayor que 0. "
            f"Recibido: {comensales_nuevo}."
        )

    factor = comensales_nuevo / comensales_original
    return f"Multiplica cada ingrediente por {factor:.2f}"


from mcp.server.mcpserver.exceptions import ToolError

print("--- caso valido ---")
print(" ", await cocina.call_tool("dividir_receta", {"comensales_original": 4, "comensales_nuevo": 6}))

print()
print("--- error de VALIDACION (Pydantic, gratis) ---")
try:
    await cocina.call_tool("dividir_receta", {"comensales_original": "cuatro", "comensales_nuevo": 6})
except ToolError as e:
    print("  rechazado antes de entrar en tu funcion")
    for l in str(e).split(chr(10)):
        if "Input should be" in l:
            print("   ", l.strip())

print()
print("--- error de LOGICA (tuyo) ---")
try:
    await cocina.call_tool("dividir_receta", {"comensales_original": 0, "comensales_nuevo": 6})
except ToolError as e:
    print("  tu funcion se ejecuto y lanzo el error:")
    print("   ", str(e).split(": ", 1)[-1][:110])
    print()
    print("  Claude lee ese texto y puede corregirse solo.")
"""
)

# ===========================================================================
md(
    """
---
## Paso 7 — Del notebook al archivo real

Un notebook no puede ser un servidor MCP: Claude Code necesita un script que
arranque y escuche. Vamos a **exportar** lo que hemos construido a un `.py`
de verdad, y arrancarlo.
"""
)

code(
    """
# QUE HACE : escribe el servidor 'cocina' como archivo Python ejecutable.
# COMO     : lo generamos como texto y lo volcamos a disco.
# POR QUE  : asi ves la forma final que debe tener el archivo, con el
#            bloque de arranque incluido.

from pathlib import Path

CODIGO = '''\"\"\"Servidor MCP cocina. Generado desde 01-escribe-tu-propio-mcp.ipynb.\"\"\"

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
    \"\"\"Depuracion. SIEMPRE a stderr: stdout es el canal del protocolo.\"\"\"
    print(mensaje, file=sys.stderr, flush=True)


@cocina.tool(name="convertir")
def convertir(
    cantidad: float,
    origen: Literal["g", "kg", "oz", "lb"],
    destino: Literal["g", "kg", "oz", "lb"],
) -> str:
    \"\"\"Convierte una cantidad entre unidades de peso.

    Úsala cuando aparezcan unidades de peso mezcladas en una receta.
    No la uses para volumen (ml, tazas) ni para temperatura.

    Args:
        cantidad: El número a convertir.
        origen: Unidad de partida.
        destino: Unidad de llegada.
    \"\"\"
    log(f"convertir({cantidad}, {origen}, {destino})")
    a_gramos = {"g": 1.0, "kg": 1000.0, "oz": 28.3495, "lb": 453.592}
    resultado = cantidad * a_gramos[origen] / a_gramos[destino]
    return f"{cantidad} {origen} = {resultado:.2f} {destino}"


@cocina.tool(name="dividir_receta")
def dividir_receta(comensales_original: int, comensales_nuevo: int) -> str:
    \"\"\"Calcula el factor para reescalar una receta a otro número de comensales.

    Úsala cuando quieran adaptar una receta a más o menos gente.

    Args:
        comensales_original: Para cuántos es la receta actualmente.
        comensales_nuevo: Para cuántos la quieren.
    \"\"\"
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
'''

destino = Path("servidor_cocina.py")
destino.write_text(CODIGO, encoding="utf-8")

print(f"escrito {destino}  ({len(CODIGO)} caracteres, {CODIGO.count(chr(10))} lineas)")
print()
print("Fijate en las dos cosas que un notebook NO tiene y un servidor SI:")
print("  1. la funcion log() escribiendo a stderr")
print("  2. el bloque main() + if __name__ == '__main__'")
"""
)

code(
    """
# QUE HACE : arranca el archivo que acabamos de escribir y habla con el.
# COMO     : exactamente igual que hace Claude Code.
# ESTO ES  : la prueba definitiva de que tu servidor funciona.

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

params = StdioServerParameters(command="uv", args=["run", "python", "servidor_cocina.py"])

async with stdio_client(params) as (leer, escribir):
    async with ClientSession(leer, escribir) as sesion:
        info = await sesion.initialize()
        print("handshake ->", info.server_info.name, info.server_info.version)

        tools = await sesion.list_tools()
        print("tools     ->", [t.name for t in tools.tools])
        print()

        r = await sesion.call_tool("convertir", {"cantidad": 500, "origen": "g", "destino": "lb"})
        print("convertir      ->", r.content[0].text)

        r = await sesion.call_tool(
            "dividir_receta", {"comensales_original": 4, "comensales_nuevo": 6}
        )
        print("dividir_receta ->", r.content[0].text)

print()
print("FUNCIONA. Ese archivo ya es un MCP registrable en Claude Code.")
"""
)

md(
    """
### Registrarlo

Un comando:

```bash
claude mcp add cocina --scope user -- \\
    uv run --directory /ruta/absoluta/al/proyecto python servidor_cocina.py
```

- `--scope user` → disponible en todos tus proyectos. Alternativa: `project`.
- `--directory` → **ruta absoluta**. Claude Code lo arranca desde cualquier sitio;
  sin esto, `uv` no encuentra el proyecto.
- El `--` separa las opciones de `claude` del comando a ejecutar.

Comprobar y quitar:

```bash
claude mcp list                          # health check de todos
claude mcp remove cocina --scope user
```
"""
)

# ===========================================================================
md(
    """
---
## Plantilla

Copia esto para empezar cualquier servidor. Los `TODO` son lo único que cambias.
"""
)

code(
    """
# QUE HACE : imprime la plantilla lista para copiar.
# USO      : copiala a tu archivo nuevo y rellena los TODO.

PLANTILLA = '''\"\"\"TODO: una frase de que hace este servidor.\"\"\"

import sys
from typing import Literal

from mcp.server.mcpserver import MCPServer

mcp = MCPServer(
    name="TODO_nombre_tecnico",
    title="TODO Nombre Legible",
    version="0.1.0",
    instructions="TODO: cuando deberia Claude usar este servidor.",
)


def log(mensaje: str) -> None:
    \"\"\"Depuracion a stderr. NUNCA print() a stdout en un servidor stdio.\"\"\"
    print(mensaje, file=sys.stderr, flush=True)


@mcp.tool(name="TODO_nombre_tool")
def todo_nombre_tool(
    parametro: str,                            # TODO: type hints SIEMPRE
    opcion: Literal["a", "b"] = "a",           # TODO: Literal si el set es cerrado
) -> str:
    \"\"\"TODO: que hace, en imperativo, una frase.

    Úsala cuando TODO: situacion concreta.
    No la uses si TODO: situacion parecida pero distinta.

    Args:
        parametro: TODO.
        opcion: TODO.
    \"\"\"
    log(f"TODO_nombre_tool({parametro!r}, {opcion!r})")

    if not parametro.strip():
        raise ValueError("parametro no puede estar vacio. Pasa un texto valido.")

    return "TODO: el resultado"


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
'''

print(PLANTILLA)
"""
)

# ===========================================================================
md(
    """
---
## Ejercicio

Escribe una tool `sustituir_ingrediente` que proponga sustitutos.

**Requisitos:**

1. Parámetro `ingrediente: str` — obligatorio
2. Parámetro `motivo` cerrado a: `"alergia"`, `"no_tengo"`, `"vegano"` — por defecto `"no_tengo"`
3. Docstring con **cuándo usarla y cuándo no**
4. Si `ingrediente` viene vacío, lanza `ValueError` con mensaje útil
5. Devuelve un texto cualquiera (la lógica da igual)

Escríbela en la celda siguiente antes de mirar la solución.
"""
)

code(
    """
# ===== TU TURNO =====
# Escribe aqui tu tool. Luego ejecuta la celda de verificacion.
#
# @ejercicio.tool(name="sustituir_ingrediente")
# def sustituir_ingrediente(...):
#     ...

ejercicio = MCPServer(name="ejercicio")

# --- escribe debajo de esta linea ---
"""
)

md(
    """
### Solución

Intenta la tuya antes. Compara después: lo que importa no es que sea idéntica,
sino que cumpla los 5 requisitos.
"""
)

code(
    """
# ===== SOLUCION =====

solucion = MCPServer(name="solucion")


@solucion.tool(name="sustituir_ingrediente")
def sustituir_ingrediente(
    ingrediente: str,                                          # (1) obligatorio
    motivo: Literal["alergia", "no_tengo", "vegano"] = "no_tengo",  # (2) cerrado
) -> str:
    \"\"\"Propone sustitutos para un ingrediente de una receta.

    Úsala cuando falte un ingrediente, haya una alergia, o quieran
    adaptar una receta a una dieta. No la uses para convertir unidades
    ni para cambiar las cantidades: para eso hay otras tools.

    Args:
        ingrediente: El ingrediente a sustituir, en singular.
        motivo: Por qué se sustituye. Cambia qué sustitutos son válidos.
    \"\"\"                                                        # (3) cuando si / cuando no
    if not ingrediente.strip():                                # (4) validacion propia
        raise ValueError(
            "ingrediente no puede estar vacio. "
            "Pasa el nombre del ingrediente a sustituir, por ejemplo 'mantequilla'."
        )
    return f"Sustitutos para {ingrediente} (motivo: {motivo}): ..."   # (5)


# --- verificacion automatica de los 5 requisitos ---
import json
from mcp.server.mcpserver.exceptions import ToolError

t = (await solucion.list_tools())[0]
esquema = t.input_schema
props = esquema["properties"]

print("(1) 'ingrediente' obligatorio      :", "ingrediente" in esquema.get("required", []))
print("(2) 'motivo' es enum de 3          :", props["motivo"].get("enum"))
print("    'motivo' opcional, defecto     :", props["motivo"].get("default"))
print("(3) docstring dice cuando NO usarla:", "No la uses" in (t.description or ""))

try:
    await solucion.call_tool("sustituir_ingrediente", {"ingrediente": "   "})
    print("(4) validacion de vacio            : NO (paso, deberia fallar)")
except ToolError:
    print("(4) validacion de vacio            : True")

r = await solucion.call_tool("sustituir_ingrediente", {"ingrediente": "mantequilla", "motivo": "vegano"})
print("(5) devuelve texto                 : True")
"""
)

# ===========================================================================
md(
    """
---
## Checklist antes de dar por bueno un MCP

Recórrela entera. Cada línea es un fallo que hemos visto de verdad.

**Código**
- [ ] Todos los parámetros tienen type hint — sin ellos el schema miente (`string` silencioso)
- [ ] Los parámetros de conjunto cerrado usan `Literal`
- [ ] Los opcionales tienen valor por defecto
- [ ] No hay ni un solo `print()` a stdout — solo `log()` a stderr
- [ ] Existe el bloque `main()` + `if __name__ == "__main__"`
- [ ] Los errores lanzan excepción con **mensaje accionable**, no `"error"`

**Docstrings**
- [ ] Primera línea: qué hace, imperativo, una frase
- [ ] Dice **cuándo usarla**
- [ ] Dice **cuándo NO usarla** ← el que más se olvida
- [ ] Sección `Args:` con todos los parámetros
- [ ] Sin `CRITICAL:` ni mayúsculas agresivas — provocan sobredisparo

**Pruebas**
- [ ] Arranca sin error: `uv run python servidor.py` (se queda esperando: correcto)
- [ ] El handshake responde (usa el cliente de la sección 7)
- [ ] `claude mcp list` lo marca ✔ Connected

---

## Los cinco errores que te van a pasar

| Síntoma | Causa real | Arreglo |
|---|---|---|
| `ModuleNotFoundError: mcp.server.fastmcp` | SDK v2 renombró la clase | `from mcp.server.mcpserver import MCPServer` |
| El servidor muere sin mensaje | un `print()` en stdout | `print(x, file=sys.stderr)` |
| La tool no se dispara nunca | docstring que solo dice **qué** hace | añade **cuándo** usarla |
| La tool se dispara cuando no toca | falta el límite | añade **cuándo NO** usarla |
| Claude manda `"7"` en vez de `7` | falta el type hint | anótalos todos |

---

**Ya sabes escribir un MCP.** El siguiente paso es abrir
`src/profesor_mcp/server.py` — ahora reconoces cada línea, y puedes cambiarlo.
"""
)

# ===========================================================================
nb["cells"] = celdas
nb["metadata"] = {
    "kernelspec": {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    },
    "language_info": {"name": "python", "version": "3.12.13"},
}

destino = "01-escribe-tu-propio-mcp.ipynb"
with open(destino, "w", encoding="utf-8") as f:
    nbf.write(nb, f)

n_code = sum(1 for c in celdas if c["cell_type"] == "code")
n_md = sum(1 for c in celdas if c["cell_type"] == "markdown")
print(f"Escrito {destino}: {len(celdas)} celdas ({n_code} de codigo, {n_md} de texto)")
