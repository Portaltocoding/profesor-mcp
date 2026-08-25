# profesor-mcp

Servidor MCP que impone una prosa clara, directa y explicativa.

> **Empieza por los notebooks.** Son ejecutables y ya vienen con las salidas
> guardadas, así que puedes leerlos sin correr nada.
>
> | Notebook | Para qué | Celdas |
> |---|---|---|
> | `00-anatomia-de-un-mcp.ipynb` | **Entender** qué es un MCP. Glosario de 20 términos, el protocolo crudo, tres fallos reproducidos en vivo. | 32 |
> | `01-escribe-tu-propio-mcp.ipynb` | **Escribir** el tuyo. Receta de 7 pasos, sintaxis etiquetada pieza a pieza, plantilla y ejercicio autocorregido. | 28 |
>
> ```bash
> uv run jupyter lab
> ```

---

## De qué se compone y cómo funciona un MCP

### Las tres capas

```
  ┌─────────────────────────────────────────────┐
  │  HOST  (Claude Code / la app de Claude)      │  ← decide qué llamar
  │                                              │
  │   ┌──────────────────────────────────────┐   │
  │   │  CLIENTE  (uno por cada servidor)    │   │  ← habla el protocolo
  │   └──────────────┬───────────────────────┘   │
  └──────────────────┼───────────────────────────┘
                     │  JSON-RPC 2.0 sobre stdin/stdout
                     ▼
  ┌─────────────────────────────────────────────┐
  │  SERVIDOR  (esto es lo que escribes tú)      │  ← hace el trabajo
  │   tools · prompts · resources                │
  └─────────────────────────────────────────────┘
```

- **Host**: la aplicación. Gestiona la conversación y decide.
- **Cliente**: el conector. Hay uno por servidor. Tú no lo escribes.
- **Servidor**: tu código. Un proceso que escucha y responde.

### El transporte

Este servidor usa **stdio**. Claude Code lo lanza como subproceso y le habla
por la entrada/salida estándar. No hay puertos, no hay HTTP, no hay red.

**Consecuencia crítica:** `print()` escribe en stdout, que es el canal del
protocolo. Un solo `print()` corrompe un mensaje y tumba el servidor.
Para depurar → `stderr`. En este proyecto está la función `log()`.

La alternativa es `streamable-http`, para servidores remotos. Mismo protocolo,
distinto tubo.

### El ciclo de vida

```
1. ARRANQUE       host lanza el proceso
2. INITIALIZE     cliente → servidor: "hola, hablo protocolo X"
                  servidor → cliente: "hola, soy profesor v0.1.0"
3. INITIALIZED    cliente → servidor: notificación, sin respuesta
4. DESCUBRIMIENTO cliente → servidor: tools/list, prompts/list
                  el host mete las descripciones en el contexto de Claude
5. USO            cliente → servidor: tools/call {name, arguments}
                  servidor → cliente: {content: [...]}
6. CIERRE         host mata el proceso
```

Los pasos 2 y 3 son obligatorios y van primero. Cualquier otra llamada antes
del handshake se rechaza.

### Las tres primitivas

| Primitiva | Quién la dispara | Para qué |
|---|---|---|
| **Tool** | Claude, solo | Acciones. Claude decide si aplica. |
| **Prompt** | Tú, con `/nombre` | Plantillas. Control explícito. |
| **Resource** | La app | Datos que el host lee (archivos, registros). |

La diferencia tool/prompt es de **control**, no de capacidad. Este servidor
expone las dos con el mismo contenido, precisamente para que compares.

---

## Qué hace este servidor en concreto

Un MCP **no puede** cambiar cómo piensa Claude de forma global — eso son los
output styles o el `CLAUDE.md`. Lo que sí puede es entregarle, en el momento
justo, un **andamiaje**: una estructura de explicación que Claude rellena.

El andamiaje de `profesor` tiene seis pasos:

1. Qué es — una frase
2. El modelo mental — analogía, y dónde se rompe
3. El mecanismo — paso a paso causal
4. Ejemplo mínimo — el caso más pequeño que aún es real
5. Cómo falla — los errores típicos y su síntoma
6. Comprobación — una pregunta de razonamiento

Más reglas de prosa: frases cortas, voz activa, cero relleno, sin pedir permiso.

Tres niveles: `novato` · `intermedio` · `avanzado`.

---

## Estructura del proyecto

```
profesor-mcp/
├── pyproject.toml              # dependencias + declara el comando profesor-mcp
├── src/profesor_mcp/
│   ├── __init__.py             # reexporta main() para el comando
│   └── server.py               # EL SERVIDOR. Fuente de verdad de los moldes.
│
├── generar_ts.py               # server.py  ──►  ts/src/moldes.ts
├── ts/                         # el gemelo en TypeScript (paquete npm)
│   ├── package.json
│   └── src/
│       ├── moldes.ts           # GENERADO. No se edita.
│       └── server.ts           # la mecánica, escrita a mano
│
├── probar.py                   # cliente de prueba: arranca el server y lo interroga
├── probar_dialogo.py           # recorre las ramas de la cascada del diálogo
├── probar_paridad.py           # Python vs TypeScript, byte a byte
│
├── metodo_manual.py            # derivación del MOLDE_MANUAL y su evidencia
├── 00-anatomia-de-un-mcp.ipynb # entender el protocolo
└── 01-escribe-tu-propio-mcp.ipynb  # escribir el tuyo
```

`server.py` por bloques:

| Bloque | Qué contiene |
|---|---|
| 1 | Imports. `MCPServer` (antes `FastMCP`), `Literal`, `sys`. |
| 2 | La instancia + `log()` a stderr. |
| 3 | `ANDAMIAJE` y `NIVELES`. El contenido pedagógico. |
| 4 | `@mcp.tool()` → `explicar`. El docstring es lo que lee Claude. |
| 5 | `@mcp.prompt()` → `profesor`. Lo invocas tú. |
| 6 | `main()` → `mcp.run(transport="stdio")`. Bucle infinito. |

---

## Instalación

El servidor existe **dos veces**: en Python y en TypeScript. Hacen exactamente
lo mismo y devuelven el mismo texto. Elige según lo que ya tengas instalado.

```bash
# Python — desde PyPI
claude mcp add profesor --scope user -- uvx profesor-mcp

# Node — desde npm
claude mcp add profesor --scope user -- npx -y profesor-mcp
```

`uvx` es a `uv` lo que `npx` a npm: descarga el paquete, lo aísla y lo ejecuta.
No hace falta clonar el repositorio.

En cualquier otro cliente MCP (app de Claude, Cursor, Zed, Cline…), el bloque
equivalente en su fichero de configuración:

```json
{
  "mcpServers": {
    "profesor": { "command": "uvx", "args": ["profesor-mcp"] }
  }
}
```

Requisitos: Python ≥ 3.12 con [uv](https://docs.astral.sh/uv/), o Node ≥ 18.
Funciona en Linux, macOS y Windows: no hay nada específico de plataforma en
ninguna de las dos versiones. En Windows, si los acentos salen rotos en la
versión de Python, añade `"env": {"PYTHONUTF8": "1"}`.

### Por qué dos paquetes y no uno

npm y PyPI no son sitios donde se publican MCPs: son registros de lenguaje, y
cada uno trae su intérprete detrás. Node no ejecuta Python. MCP en cambio no
tiene lenguaje —es JSON-RPC por stdin/stdout— así que el host no distingue una
versión de la otra: lanza un comando y le manda JSON.

La alternativa habitual, publicar en npm un envoltorio JavaScript que llame a
Python por debajo, obligaría a tener Node *y* Python instalados a cambio de
nada. Aquí las dos son nativas.

### Cómo se evita que se separen

Los moldes son 385 líneas de prosa y son el valor del proyecto. Si vivieran en
los dos sitios, se bifurcarían. No hay dos copias: hay una fuente y una
derivación.

```
  src/profesor_mcp/server.py   ← los moldes se escriben AQUI, y solo aquí
            │
            │  uv run python generar_ts.py
            ▼
      ts/src/moldes.ts         ← generado. Editarlo no sirve de nada.
```

`probar_paridad.py` lo verifica: lanza los dos servidores, recorre las 61
combinaciones de método, nivel, tono y extensión, y compara los textos byte a
byte. Lo único escrito dos veces es la mecánica del diálogo, porque cada SDK
tiene la suya.

---

## Cómo se usa

```bash
# probar sin Claude Code
uv run python probar.py

# arrancar a mano (no verás nada: espera JSON en stdin — eso es correcto)
uv run profesor-mcp
```

En Claude Code, ya registrado en scope `user`:

- La tool `explicar` se dispara sola cuando preguntas algo del tipo "qué es X".
- El prompt lo llamas tú con `/profesor`.

Para quitarlo: `claude mcp remove profesor --scope user`

---

## Trampas que ya nos mordieron

| Síntoma | Causa | Solución |
|---|---|---|
| `ModuleNotFoundError: mcp.server.fastmcp` | SDK v2 renombró la clase | `from mcp.server.mcpserver import MCPServer` |
| `AttributeError: serverInfo` | El SDK v2 usa snake_case | `server_info`, `input_schema` |
| El servidor muere sin mensaje | Un `print()` en stdout | Usa `log()` → stderr |
| Se pierde la última respuesta | stdin cerró antes de responder | Usa un cliente real, no `echo \| pipe` |
| La tool nunca se dispara | Docstring vago | El docstring dice **cuándo** usarla |
| `requires-python` falla | Python 3.9 del sistema | `uv python install 3.12` |

---

## Cómo extenderlo

Añadir una tool son cuatro líneas:

```python
@mcp.tool(name="refutar")
def refutar(afirmacion: str) -> str:
    """Devuelve la estructura para atacar una afirmación.

    Úsala cuando alguien quiera poner a prueba una idea, no entenderla.
    """
    return f"Ataca **{afirmacion}** así: 1) ¿qué la haría falsa? ..."
```

El decorador lee la firma y genera el schema. Los type hints **no son opcionales**:
sin ellos el schema sale sin tipos y Claude manda cualquier cosa.
