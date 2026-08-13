"""Genera el notebook didactico 00-anatomia-de-un-mcp.ipynb.

QUE HACE : construye el .ipynb celda por celda.
COMO     : un .ipynb es JSON. Escribirlo a mano es pedir errores de escapado.
           nbformat lo construye con objetos Python y lo serializa bien.
USO      : uv run python construir_notebook.py
"""

import nbformat as nbf

nb = nbf.v4.new_notebook()
celdas = []


def md(texto: str) -> None:
    """Anade una celda de texto (markdown)."""
    celdas.append(nbf.v4.new_markdown_cell(texto.strip()))


def code(texto: str) -> None:
    """Anade una celda ejecutable (python)."""
    celdas.append(nbf.v4.new_code_cell(texto.strip()))


# ===========================================================================
md(
    """
# Anatomía de un MCP

Notebook ejecutable. Cada celda de código **corre de verdad**: verás el schema
generarse, el JSON viajar, y los errores ocurrir.

**Ejecútalas en orden** — algunas dependen de las anteriores.

```bash
uv run jupyter lab 00-anatomia-de-un-mcp.ipynb
```
"""
)

# ===========================================================================
md(
    """
---
## Glosario

Todo el vocabulario que aparece, definido antes de usarlo.

### El protocolo

**MCP (Model Context Protocol)**
Estándar abierto para conectar modelos de lenguaje con herramientas y datos
externos. Define *cómo* se habla, no *qué* se dice.

**JSON-RPC 2.0**
El formato de los mensajes. Cada mensaje es un objeto JSON con `method` (qué
quiero), `params` (con qué datos) e `id` (para emparejar pregunta y respuesta).
Es un estándar de 2010, anterior a MCP; MCP simplemente lo reutiliza.

**Petición (request)**
Mensaje **con** `id`. Exige respuesta.

**Notificación (notification)**
Mensaje **sin** `id`. No espera respuesta. Se usa para avisos de una sola vía.

**Transporte**
El tubo físico por donde viajan los mensajes. MCP define dos:
- **stdio** — entrada/salida estándar de un subproceso. Para servidores locales.
- **streamable-http** — HTTP. Para servidores remotos.

**Handshake**
El saludo inicial obligatorio: `initialize` → respuesta → `notifications/initialized`.
Hasta que termina, ninguna otra llamada es válida.

### Los actores

**Host**
La aplicación que contiene al modelo. Claude Code, la app de Claude. Decide
qué servidores lanzar y qué llamadas permitir.

**Cliente**
El conector que habla el protocolo. Hay **uno por cada servidor**. Vive dentro
del host. No lo escribes tú.

**Servidor**
Tu código. Un proceso que escucha mensajes y responde. Esto es lo que construyes.

### Las primitivas

**Tool (herramienta)**
Una función que **Claude decide** llamar. Model-controlled. Claude lee su
descripción y decide si aplica.

**Prompt**
Una plantilla que **tú invocas** con `/nombre`. User-controlled. No se dispara sola.

**Resource (recurso)**
Datos que el host puede leer, identificados por URI. Application-controlled.

### El schema

**JSON Schema**
Un lenguaje para describir la forma de un dato: qué campos tiene, de qué tipo,
cuáles son obligatorios. Claude lee el schema de cada tool para saber cómo llamarla.

**Type hint (anotación de tipo)**
La sintaxis `tema: str` en Python. Normalmente es documentación que Python ignora.
Aquí **no**: el SDK la lee para generar el JSON Schema. Sin type hints no hay schema.

**Literal**
Un type hint que restringe a valores exactos: `Literal["a", "b"]` significa
"solo estos dos strings". Se traduce a un `enum` en el JSON Schema.

**Pydantic**
La librería que valida los datos contra el schema. Si Claude manda algo que no
encaja, Pydantic lo rechaza antes de que tu función se ejecute.

### Del SDK

**MCPServer**
La clase principal del SDK de Python (v2). En la v1 se llamaba `FastMCP`.
Mismo objeto, otro nombre. Los tutoriales antiguos usan el nombre viejo.

**Decorador**
La sintaxis `@algo` encima de una función. Es una función que recibe tu función
y la registra o la modifica. `@mcp.tool()` registra tu función como herramienta.

**Docstring**
El string entre triples comillas al principio de una función. En un MCP **no es
documentación**: es el texto que lee Claude para decidir si usar la tool.
"""
)

# ===========================================================================
md(
    """
---
## 1. El entorno

Comprobamos qué versiones tenemos. El SDK de MCP exige Python 3.10 o superior.
"""
)

code(
    """
# QUE HACE : imprime las versiones para confirmar que el entorno es el correcto.
# FALLA SI : Python < 3.10 -> el SDK ni siquiera se instala.
import sys
import importlib.metadata as md

print("Python :", sys.version.split()[0])
print("SDK mcp:", md.version("mcp"))
print()
print("stdout de este notebook:", sys.stdout)
print("(ojo a esto: aqui print() es seguro. En el servidor NO. Ver seccion 8.)")
"""
)

# ===========================================================================
md(
    """
---
## 2. La anatomía

```
  ┌──────────────────────────────────────────────┐
  │  HOST — Claude Code                          │
  │  decide qué llamar y cuándo                  │
  │                                              │
  │   ┌──────────────────────────────────────┐   │
  │   │  CLIENTE — uno por servidor          │   │
  │   │  traduce a JSON-RPC                  │   │
  │   └──────────────┬───────────────────────┘   │
  └──────────────────┼───────────────────────────┘
                     │
                     │   JSON-RPC 2.0
                     │   por stdin/stdout
                     │
                     ▼
  ┌──────────────────────────────────────────────┐
  │  SERVIDOR — tu código                        │
  │                                              │
  │   tools      ← las llama Claude              │
  │   prompts    ← los llamas tú                 │
  │   resources  ← los lee la app                │
  └──────────────────────────────────────────────┘
```

**La diferencia con una app web:** no hay puerto, no hay URL, no hay red.
El host lanza tu script como subproceso y le escribe por la entrada estándar.
Es el mismo mecanismo que `cat archivo | grep algo`.
"""
)

# ===========================================================================
md(
    """
---
## 3. La sintaxis: qué es de Python y qué es del SDK

Viniendo de TSX, al ver una tool no es obvio qué pieza es del lenguaje y cuál
la aporta la librería. Etiquetemos todo antes de escribir nada.

```python
@demo.tool(name="saludar")            # (1) (2) (3)
def saludar(                          # (4)
    nombre: str,                      # (5)
    idioma: Literal["es","en","fr"]   # (6)
        = "es",                       # (7)
) -> str:                             # (8)
    \"\"\"Saluda a una persona.        # (9)

    Args:                             # (10)
        nombre: A quién saludar.
    \"\"\"
    return f"Hola, {nombre}"          # (11)
```

| # | Sintaxis | Cómo se llama | ¿De quién es? | Si lo quitas |
|---|---|---|---|---|
| 1 | `@` | **decorador** | **Python** — el símbolo | La función existe pero Claude no la ve |
| 2 | `demo.tool` | método del SDK | **SDK** | — |
| 3 | `(name="saludar")` | argumento con nombre | **Python** | El nombre sale de la función: `saludar` |
| 4 | `def` | definición de función | **Python** | No hay función |
| 5 | `nombre: str` | **type hint** (anotación) | **Python**, pero el SDK **lo lee** | El schema dice `string` por defecto — silencioso y falso |
| 6 | `Literal[...]` | type hint restringido | **Python** (`typing`) | El parámetro acepta cualquier texto |
| 7 | `= "es"` | valor por defecto | **Python** | El parámetro pasa a ser obligatorio |
| 8 | `-> str` | anotación de retorno | **Python** | Nada — el SDK no la usa para el schema |
| 9 | `\"\"\"...\"\"\"` | **docstring** | **Python**, pero el SDK **lo lee** | Claude no sabe cuándo llamar la tool |
| 10 | `Args:` | convención de formato | **convención**, no sintaxis | Nada roto, pero se lee peor |
| 11 | `f"...{x}"` | **f-string** | **Python** | Tendrías que concatenar a mano |

**Lo que hay que retener:** casi todo es Python normal. El SDK solo aporta el
método `.tool()`. Lo insólito es que **el SDK lee cosas que Python normalmente
ignora**: los type hints y el docstring. En Python puro son decoración. Aquí
son la interfaz con Claude.
"""
)

code(
    """
# QUE HACE : construye un decorador desde cero para ver que no tiene magia.
# POR QUE  : '@algo' asusta hasta que ves que es solo una funcion.

registro = {}

# Un decorador es una funcion que:
def registrar(func):                  # 1. RECIBE una funcion como argumento
    registro[func.__name__] = func    # 2. HACE algo con ella (aqui: guardarla)
    return func                       # 3. LA DEVUELVE, normalmente intacta


# --- forma A: con la sintaxis @ ---
@registrar
def sumar(a, b):
    return a + b


# --- forma B: a mano, SIN la @ ---
def restar(a, b):
    return a - b

restar = registrar(restar)   # <-- esto es EXACTAMENTE lo que hace la @


print("registradas:", list(registro.keys()))
print()
print("Las dos formas son identicas. La @ es solo azucar sintactico.")
print("   @registrar          es igual a      f = registrar(f)")
print()
print("Y ojo: las funciones siguen funcionando normal.")
print("   sumar(2, 3)  ->", sumar(2, 3))
print("   restar(5, 2) ->", restar(5, 2))
"""
)

md(
    """
### Con paréntesis y sin paréntesis

Esta distinción confunde a todo el mundo:

| Forma | Qué significa |
|---|---|
| `@registrar` | `registrar` **es** el decorador. Recibe la función directo. |
| `@demo.tool()` | `demo.tool()` **devuelve** el decorador. Se ejecuta primero. |

Un decorador que acepta configuración necesita paréntesis: primero se llama con
la config, y lo que devuelve es el decorador de verdad. Se llama *decorator factory*
— una fábrica de decoradores.

Por eso `@demo.tool()` lleva paréntesis aunque no le pases nada.
"""
)

code(
    """
# QUE HACE : demuestra la diferencia entre decorador y fabrica de decoradores.

# --- decorador simple: recibe la funcion directamente ---
def simple(func):
    print("   [simple] me han pasado la funcion:", func.__name__)
    return func


# --- fabrica: recibe config, DEVUELVE un decorador ---
def fabrica(etiqueta):
    print(f"   [fabrica] me han pasado la config: {etiqueta!r}")

    def decorador_real(func):
        print("   [fabrica] ahora si, la funcion:", func.__name__)
        return func

    return decorador_real   # <-- lo que se aplica a la funcion


print("Usando @simple  (SIN parentesis):")

@simple
def uno():
    pass

print()
print("Usando @fabrica('hola')  (CON parentesis):")

@fabrica("hola")
def dos():
    pass

print()
print("Fijate en el ORDEN de los mensajes de la fabrica:")
print("  1. se ejecuta fabrica('hola')      -> devuelve decorador_real")
print("  2. se aplica decorador_real a dos  -> registra la funcion")
print()
print("@demo.tool() es una fabrica. Por eso lleva parentesis.")
print("FALLA SI escribes @demo.tool sin parentesis -> el SDK recibe tu")
print("funcion donde esperaba la config, y revienta o se comporta raro.")
"""
)

md(
    """
### `async` y `await`

Los vas a ver a partir de la sección 5. En dos frases:

- **`async def`** — declara una función que puede pausarse a mitad.
- **`await`** — pausa aquí hasta que esto termine, y mientras deja correr otras cosas.

Un servidor MCP atiende varias peticiones a la vez, así que el SDK es asíncrono
por dentro. **Tus tools no tienen que serlo**: `saludar` es un `def` normal y
funciona. Solo necesitas `async def` si dentro haces algo que también es
asíncrono (una petición HTTP, una consulta a base de datos).

En un notebook puedes escribir `await` directamente en una celda. En un script
normal no: necesitas `asyncio.run()`.
"""
)

# ===========================================================================
md(
    """
---
## 4. El servidor mínimo

Tres líneas. Creamos la instancia y miramos qué tiene dentro.
"""
)

code(
    """
# QUE HACE : crea un servidor MCP vacio.
# COMO     : MCPServer es la clase principal. En el SDK v1 se llamaba FastMCP.
# FALLA SI : usas 'from mcp.server.fastmcp import FastMCP' -> ModuleNotFoundError
#            en el SDK v2. Es el error mas comun al seguir tutoriales viejos.
from mcp.server.mcpserver import MCPServer

demo = MCPServer(
    name="demo",          # identificador tecnico. Debe ser unico entre servidores.
    title="Servidor demo",  # nombre legible para humanos.
    version="0.1.0",
)

print("nombre  :", demo.name)
print("titulo  :", demo.title)
print("version :", demo.version)
print()
print("Ya es un servidor MCP valido. No hace nada todavia, pero arranca.")
"""
)

# ===========================================================================
md(
    """
---
## 5. Una tool, y el schema que genera sola

Aquí está la parte que más sorprende. Escribes una función Python normal.
El decorador **lee la firma** y construye el JSON Schema automáticamente.

Ese schema es lo **único** que Claude ve. No ve tu código.
"""
)

code(
    """
from typing import Literal

# QUE HACE : registra 'saludar' como herramienta del servidor demo.
# COMO     : el decorador inspecciona la firma (nombres + type hints) y
#            genera un JSON Schema. Tambien lee el docstring como descripcion.
# CLAVE    : el docstring NO es documentacion. Es lo que lee Claude para
#            decidir SI llamar la tool. Un docstring vago = tool que no se usa.

@demo.tool(name="saludar")
def saludar(
    nombre: str,
    idioma: Literal["es", "en", "fr"] = "es",
) -> str:
    \"\"\"Saluda a una persona en el idioma indicado.

    Úsala cuando alguien pida un saludo personalizado.

    Args:
        nombre: A quién saludar.
        idioma: Código del idioma. es=español, en=inglés, fr=francés.
    \"\"\"
    saludos = {"es": "Hola", "en": "Hello", "fr": "Bonjour"}
    return f"{saludos[idioma]}, {nombre}!"


print("Tool registrada.")
print("Fijate en que 'saludar' sigue siendo una funcion normal de Python:")
print("  llamada directa ->", saludar("Nuria", "fr"))
"""
)

code(
    """
# QUE HACE : muestra el JSON Schema que el decorador genero solo.
# COMO     : list_tools() es asincrona -> usamos 'await' directo.
#            En un notebook eso funciona. En un script normal necesitarias
#            asyncio.run(). FALLA SI usas asyncio.run() aqui: ya hay un
#            bucle de eventos corriendo -> RuntimeError.
import json

tools = await demo.list_tools()
t = tools[0]

print("nombre      :", t.name)
print("descripcion :", (t.description or "").split(chr(10))[0])
print()
print("--- JSON SCHEMA (esto es TODO lo que ve Claude) ---")
print(json.dumps(t.input_schema, indent=2, ensure_ascii=False))
"""
)

md(
    """
**Lee el schema con atención.** Tres cosas salieron solas de la firma de Python:

| En Python | En el schema | Efecto |
|---|---|---|
| `nombre: str` | `"type": "string"` | Claude sabe que va texto |
| `idioma: Literal["es","en","fr"]` | `"enum": [...]` | Claude **solo** puede mandar esos tres |
| `idioma = "es"` | `"default": "es"`, fuera de `required` | Claude puede omitirlo |

El `Literal` es la herramienta más útil aquí: convierte un parámetro libre en
una lista cerrada de opciones. Claude no puede inventarse un cuarto idioma.
"""
)

# ===========================================================================
md(
    """
---
## 6. Llamarla como la llama Claude

Antes la llamamos como función Python. Claude **no** hace eso: manda un mensaje
`tools/call` y recibe un resultado estructurado. Veamos la diferencia.
"""
)

code(
    """
# QUE HACE : invoca la tool a traves del servidor, no como funcion.
# COMO     : call_tool recibe el nombre y un diccionario de argumentos,
#            los valida contra el schema, y ejecuta la funcion.
# DIFERENCIA: saludar("Nuria") ejecuta la funcion.
#             call_tool("saludar", {...}) pasa por validacion + protocolo.

resultado = await demo.call_tool("saludar", {"nombre": "Nuria", "idioma": "en"})

print("tipo del resultado:", type(resultado).__name__)
print()
print("resultado crudo:", resultado)
"""
)

# ===========================================================================
md(
    """
---
## 7. El protocolo crudo

Estos son los mensajes JSON reales que viajan por el tubo. Cuatro mensajes
componen una sesión mínima completa.
"""
)

code(
    """
# QUE HACE : construye a mano los mensajes de una sesion completa.
# POR QUE  : normalmente el SDK los genera por ti y no los ves nunca.
#            Verlos una vez hace que todo lo demas tenga sentido.
import json

mensajes = [
    # 1. PETICION (tiene 'id' -> exige respuesta). Siempre la primera.
    {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2026-07-28",
            "capabilities": {},
            "clientInfo": {"name": "mi-cliente", "version": "1.0"},
        },
    },
    # 2. NOTIFICACION (sin 'id' -> no espera respuesta). Cierra el handshake.
    {"jsonrpc": "2.0", "method": "notifications/initialized"},
    # 3. PETICION. Descubrimiento: que sabe hacer este servidor.
    {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
    # 4. PETICION. Ejecucion.
    {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {"name": "saludar", "arguments": {"nombre": "Nuria"}},
    },
]

for m in mensajes:
    tipo = "PETICION    " if "id" in m else "NOTIFICACION"
    print(f"{tipo} {m['method']}")
    print("  ", json.dumps(m, ensure_ascii=False))
    print()

print("Cada mensaje va en UNA linea, terminada en salto de linea.")
print("Ese es todo el formato de cable. No hay mas.")
"""
)

# ===========================================================================
md(
    """
---
## 8. El handshake real, contra el servidor de verdad

Hasta ahora usábamos el servidor `demo` en memoria. Ahora lanzamos
`profesor-mcp` como **subproceso real** y hablamos con él por stdio.

Esto es exactamente lo que hace Claude Code al arrancar.
"""
)

code(
    """
# QUE HACE : arranca el servidor profesor como subproceso y le habla.
# COMO     : stdio_client abre los dos tubos. ClientSession los envuelve
#            en algo que habla JSON-RPC.
# FALLA SI : el comando no existe en el PATH -> FileNotFoundError.
# NOTA     : 'async with' garantiza que el subproceso se mata al salir.
#            Sin el, te quedan procesos zombis.
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

params = StdioServerParameters(
    command="uv",
    args=["run", "profesor-mcp"],
)

async with stdio_client(params) as (leer, escribir):
    async with ClientSession(leer, escribir) as sesion:
        # PASO 1 - handshake. Obligatorio y primero.
        info = await sesion.initialize()
        print("1. HANDSHAKE")
        print("   servidor :", info.server_info.name, info.server_info.version)
        print("   protocolo:", info.protocol_version)

        # PASO 2 - descubrimiento.
        tools = await sesion.list_tools()
        prompts = await sesion.list_prompts()
        print()
        print("2. DESCUBRIMIENTO")
        print("   tools    :", [x.name for x in tools.tools])
        print("   prompts  :", [x.name for x in prompts.prompts])

        # PASO 3 - ejecucion.
        r = await sesion.call_tool(
            "explicar",
            arguments={"tema": "los closures", "nivel": "novato"},
        )
        texto = r.content[0].text
        print()
        print("3. EJECUCION")
        print("   recibidos", len(texto), "caracteres")
        print()
        print("--- PRIMERAS LINEAS DE LO QUE RECIBE CLAUDE ---")
        for linea in texto.split(chr(10))[:8]:
            print("   |", linea)
"""
)

# ===========================================================================
md(
    """
---
## 9. Cómo falla

Tres fallos reales, reproducidos aquí. Estos son los que te van a morder.
"""
)

md(
    """
### Fallo 1 — Olvidar los type hints

El SDK genera el schema **desde las anotaciones de tipo**. Sin ellas no da error:
asume `string` para todo, en silencio.

Eso es peor que fallar. El schema parece correcto, Claude lo cree, y te manda
`"7"` (texto) donde tu función esperaba `7` (número).
"""
)

code(
    """
# QUE HACE : registra dos tools, una CON type hints y otra SIN.
# OBSERVA  : el segundo NO da error. Dice 'string' para todo.
#            Ese es el peligro: parece correcto y no lo es.

malo = MCPServer(name="comparacion")

@malo.tool(name="con_hints")
def con_hints(cantidad: int, activo: bool) -> str:
    \"\"\"Version correcta: tiene anotaciones de tipo.\"\"\"
    return "ok"

@malo.tool(name="sin_hints")
def sin_hints(cantidad, activo):
    \"\"\"Version rota: sin anotaciones de tipo.\"\"\"
    return "ok"

import json
for t in await malo.list_tools():
    print("===", t.name, "===")
    props = t.input_schema.get("properties", {})
    for campo, definicion in props.items():
        tipo = definicion.get("type", "<sin tipo>")
        print(f"   {campo:10} -> {tipo}")
    print()

print("FIJATE: 'sin_hints' NO dio error. Dice 'string' para los dos campos.")
print()
print("Con hints  : cantidad es integer. Claude manda 7. Pydantic valida.")
print("Sin hints  : cantidad es string.  Claude manda '7'. Pydantic lo acepta.")
print("             Tu funcion hace cantidad * 2 y obtiene '77'. Nadie avisa.")
print()
print("Por eso los type hints no son opcionales aqui: son la interfaz.")
"""
)

md(
    """
### Fallo 2 — Mandar un valor fuera del `enum`

El schema no es decorativo: Pydantic valida contra él **antes** de ejecutar tu
función. Un valor inválido se rechaza limpiamente en vez de romper tu código.
"""
)

code(
    """
# QUE HACE : llama a 'saludar' con un idioma que no existe en el Literal.
# ESPERADO : Pydantic lo rechaza. La funcion NO se ejecuta.
# POR QUE  : el Literal["es","en","fr"] se volvio un enum en el schema.
#            Pydantic valida contra el enum ANTES de llamar a tu funcion.

from mcp.server.mcpserver.exceptions import ToolError

# --- caso valido ---
r = await demo.call_tool("saludar", {"nombre": "Nuria", "idioma": "fr"})
print("VALIDO   -> idioma='fr' -> ok")

# --- caso invalido ---
try:
    await demo.call_tool("saludar", {"nombre": "Nuria", "idioma": "aleman"})
    print("INVALIDO -> paso la validacion (esto NO deberia pasar)")
except ToolError as e:
    print("INVALIDO -> idioma='aleman' -> RECHAZADO")
    print()
    # la ultima linea util del error dice exactamente que esperaba
    for linea in str(e).split(chr(10)):
        if "Input should be" in linea:
            print("   ", linea.strip())

print()
print("Tu funcion 'saludar' nunca llego a ejecutarse. El schema la protegio.")
print("Sin el Literal seria 'nombre: str, idioma: str', habria entrado,")
print("y habria reventado dentro con KeyError: 'aleman'.")
print()
print("DOS NIVELES, no los confundas:")
print("  - objeto servidor (aqui): lanza ToolError. Lo capturas tu.")
print("  - protocolo (Claude Code): se convierte en un resultado con isError=true.")
print("    Claude lo lee, entiende que fallo, y reintenta con un valor valido.")
"""
)

md(
    """
### Fallo 3 — `print()` en un servidor stdio

**Este es el que mata servidores sin dejar rastro.**

En stdio, la salida estándar **es** el canal del protocolo. Cada línea debe ser
un JSON válido. Un `print("debug")` inserta una línea que no lo es, el cliente
intenta parsearla, y todo se cae.

Lo reproducimos sin arrancar nada: simplemente parseamos las líneas como
lo haría el cliente.
"""
)

code(
    """
# QUE HACE : simula lo que ve el cliente cuando el servidor hace print().
# COMO     : el cliente lee stdout linea a linea y hace json.loads() de cada una.
import json

respuesta_valida = '{"jsonrpc":"2.0","id":1,"result":{"tools":[]}}'

print("=== SERVIDOR LIMPIO ===")
for linea in [respuesta_valida]:
    try:
        m = json.loads(linea)
        print("  OK  ->", m["method"] if "method" in m else f"respuesta id={m['id']}")
    except json.JSONDecodeError as e:
        print("  ROTO ->", e)

print()
print("=== SERVIDOR CON UN print('debug') ===")
for linea in ["debug: entrando en la funcion", respuesta_valida]:
    try:
        m = json.loads(linea)
        print("  OK  ->", f"respuesta id={m['id']}")
    except json.JSONDecodeError as e:
        print("  ROTO ->", type(e).__name__, "-", str(e)[:60])

print()
print("El cliente ve basura, no sabe que hacer, y cierra la conexion.")
print("En Claude Code esto aparece como 'server disconnected', sin mas pistas.")
print()
print("SOLUCION: escribe siempre en stderr.")
print("   import sys")
print("   print(mensaje, file=sys.stderr)")
"""
)

# ===========================================================================
md(
    """
---
## 10. Tool contra prompt

Misma capacidad, distinto **quién dispara**. Es la distinción que más cuesta
al principio.

| | Tool | Prompt |
|---|---|---|
| Quién decide | Claude | Tú |
| Cómo se invoca | sola, si aplica | `/nombre` |
| Qué lee para decidir | el docstring | nada, lo pides tú |
| Cuándo usarla | acciones que Claude debe elegir | control explícito |

El servidor `profesor` expone las dos con el mismo contenido, a propósito,
para que compares.
"""
)

code(
    """
# QUE HACE : registra un prompt y lo invoca.
# COMO     : @demo.prompt() en vez de @demo.tool().
# DIFERENCIA: este NUNCA se dispara solo. Solo si lo pides con /despedida.

@demo.prompt(name="despedida", description="Despedida formal.")
def despedida(nombre: str) -> str:
    \"\"\"Genera una despedida formal.\"\"\"
    return f"Redacta una despedida formal y breve dirigida a {nombre}."

ps = await demo.list_prompts()
print("prompts registrados:", [p.name for p in ps])
print()
for p in ps:
    print("argumentos de", p.name, ":")
    for a in (p.arguments or []):
        obligatorio = "obligatorio" if a.required else "opcional"
        print(f"   {a.name} ({obligatorio})")

print()
r = await demo.get_prompt("despedida", {"nombre": "el equipo"})
print("contenido generado:")
print("  ", r.messages[0].content.text)
"""
)

# ===========================================================================
md(
    """
---
## 11. Resumen

**Lo que has visto ejecutarse:**

1. Un servidor MCP son tres líneas: importar, instanciar, decorar.
2. El JSON Schema se genera solo, desde los **type hints**. Sin ellos el SDK
   asume `string` para todo, en silencio — no falla, miente.
3. `Literal` cierra un parámetro a una lista de opciones. Es tu mejor defensa.
4. El docstring **es** la interfaz con Claude. No es documentación.
5. El protocolo son cuatro mensajes JSON en una línea cada uno.
6. El handshake (`initialize` → `initialized`) es obligatorio y va primero.
7. Pydantic valida antes de ejecutar: los valores inválidos no llegan a tu código.
8. `print()` en stdio mata el servidor sin dejar rastro. Usa `stderr`.

**Tabla de trampas:**

| Síntoma | Causa | Solución |
|---|---|---|
| `ModuleNotFoundError: mcp.server.fastmcp` | SDK v2 renombró la clase | `from mcp.server.mcpserver import MCPServer` |
| `AttributeError: serverInfo` | SDK v2 usa snake_case | `server_info`, `input_schema` |
| `RuntimeError: event loop is running` | `asyncio.run()` en notebook | usa `await` directo |
| Servidor muere sin mensaje | un `print()` en stdout | `print(x, file=sys.stderr)` |
| Claude manda `"7"` en vez de `7` | sin type hints todo es `string` | anota **todos** los parámetros |
| La tool nunca se dispara | docstring vago | di **cuándo** usarla, no solo qué hace |

---

**Siguiente paso:** abre `src/profesor_mcp/server.py`. Ahora reconoces cada bloque.
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

destino = "00-anatomia-de-un-mcp.ipynb"
with open(destino, "w", encoding="utf-8") as f:
    nbf.write(nb, f)

n_code = sum(1 for c in celdas if c["cell_type"] == "code")
n_md = sum(1 for c in celdas if c["cell_type"] == "markdown")
print(f"Escrito {destino}: {len(celdas)} celdas ({n_code} de codigo, {n_md} de texto)")
