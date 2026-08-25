# profesor-mcp (TypeScript)

Servidor MCP que impone una prosa clara, directa y explicativa. Cinco moldes de
explicación —clásico, Cornell, Feynman, manual y libre— que se eligen en un
diálogo cuando la tool se dispara.

Gemelo exacto del paquete de Python [`profesor-mcp`](https://pypi.org/project/profesor-mcp/)
en PyPI. Misma tool, mismo prompt, mismo texto de salida. Elige el que te
convenga según lo que ya tengas instalado: Node o Python.

## Instalación

```bash
claude mcp add profesor --scope user -- npx -y profesor-mcp
```

En cualquier otro cliente MCP (app de Claude, Cursor, Zed, Cline…):

```json
{
  "mcpServers": {
    "profesor": { "command": "npx", "args": ["-y", "profesor-mcp"] }
  }
}
```

Requiere Node ≥ 18.

## Qué expone

| Primitiva | Nombre | Quién la dispara |
|---|---|---|
| tool | `explicar` | Claude, solo, cuando pides entender algo |
| prompt | `profesor` | Tú, con `/profesor` |

La tool abre un diálogo (*elicitation*) para elegir método y extensión, y
después los ejes que ese método admita: nivel y tono en el clásico, solo nivel
en el manual. Los métodos cerrados no preguntan nada, porque no tendría efecto.

Si tu cliente no sabe abrir diálogos, no se cuelga: cae a los valores por
defecto (clásico, intermedio, formal, normal) y responde igual.

## Desarrollo

Los textos de los moldes **no se editan aquí**. Viven en `src/profesor_mcp/server.py`,
en la raíz del repositorio, y se generan a este paquete:

```bash
uv run python generar_ts.py   # regenera ts/src/moldes.ts desde el Python
cd ts && npm run build
```

Para comprobar que las dos versiones siguen explicando igual:

```bash
uv run python probar_paridad.py
```

Recorre las 61 combinaciones de método, nivel, tono y extensión, y compara los
textos byte a byte contra el servidor de Python.
