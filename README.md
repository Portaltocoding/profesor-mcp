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
├── probar.py                   # cliente de prueba: arranca el server y lo interroga
└── src/profesor_mcp/
    ├── __init__.py             # reexporta main() para el comando
    └── server.py               # el servidor. 6 bloques comentados.
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

Publicado en PyPI. No hace falta clonar el repo: `uvx` lo descarga, lo aísla y
lo ejecuta, igual que `npx` con un paquete de npm.

```bash
claude mcp add profesor --scope user -- uvx profesor-mcp
```

En cualquier otro cliente MCP (app de Claude, Cursor, Zed, Cline…), el bloque
equivalente en su fichero de configuración:

```json
{
  "mcpServers": {
    "profesor": { "command": "uvx", "args": ["profesor-mcp"] }
  }
}
```

Requiere Python ≥ 3.12 y [uv](https://docs.astral.sh/uv/). Funciona en Linux,
macOS y Windows: es Python puro sobre stdio, sin nada específico de plataforma.
En Windows, si los acentos salen rotos, añade `"env": {"PYTHONUTF8": "1"}`.

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
