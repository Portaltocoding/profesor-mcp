# Manual: generador de capitulos con autoevaluacion

Diseno del sistema. El codigo va en un repo aparte; esto se queda aqui porque
aqui vive la investigacion (`metodo_manual.py`, el corpus, los prefacios).

El MCP `profesor` NO se toca. Explica en el chat, y eso lo hace bien. Este
sistema es otra cosa: produce un artefacto.

---

## 1. Que separa esto de lo que ya hay

El MCP devuelve un string a la conversacion. Este sistema tiene que:

- generar 8.000 a 15.000 palabras sin que las ultimas secciones salgan aguadas
- dejar un fichero, no texto que se pierde con la sesion
- juzgarse a si mismo y corregirse
- soportar cortes: son 30-50 llamadas largas

Nada de eso cabe en un tool de MCP.

## 2. Formato de salida

**Fuente canonica: Markdown.** LaTeX (`$...$`, `$$...$$`) y mermaid.
**Destino: PDF.** Se anade despues, sin rehacer nada, PERO solo si el Markdown
se escribe con disciplina de pagina desde la primera linea:

- ecuaciones numeradas por seccion, `(4.1)`, y citadas por numero
- nunca "la formula de arriba": en pagina impresa puede caer dos paginas atras
- figuras con numero, pie y referencia desde el texto

Esas reglas ya estan metidas en `MOLDE_MANUAL` (bloque "Notacion, formulas y
figuras"). El render a PDF (Typst o Pandoc) es un nodo final opcional.

Referencia de estetica objetivo: `Newton Laws from Morin Book.pdf` en el USB.
Ecuaciones display numeradas a la derecha, citadas como "But Eq. (3.2) gives",
vectores en negrita y escalares en cursiva, y CERO figuras en dos paginas
densas. Los diagramas se ganan el sitio.

---

## 3. Las tres capas de evaluacion

La decision de diseno que mas ahorra. Cada regla del molde cae en una capa, y
subir de capa sin necesidad es tirar dinero y meter ruido.

### Capa 1 — Regex (coste 0, exacta, no alucina)

- frases prohibidas: "se puede demostrar que", "es facil ver", "obviamente",
  "se deja como ejercicio", "por analogia con lo anterior", "es importante
  destacar", "cabe senalar", "como hemos visto", "¿quieres que profundice?"
- las 12 secciones presentes, con los titulos exactos
- ecuaciones con numero que nadie cita despues (numero = promesa incumplida)
- referencias a `(N.M)` que no existen
- figuras sin pie, o sin referencia desde la prosa
- ejercicios sin respuesta debajo
- placeholders: `foo`, `bar`, `lorem`

### Capa 2 — Codigo contra el contrato (coste 0)

La violacion mas grave del molde y la mas facil de verificar, PERO solo si el
contrato es un dato y no prosa:

```
para cada termino del inventario:
    primera_aparicion = posicion en el texto ensamblado
    seccion_declarada = contrato.inventario[termino].seccion
    si primera_aparicion < inicio(seccion_declarada):  -> ERROR
```

Mas: el inventario tiene que ser un DAG (nada de definiciones circulares) y
estar en orden topologico. Se valida ANTES de escribir una sola linea.

### Capa 3 — Juez LLM (caro, solo lo que exige leer)

- pendiente lineal: ¿hay una frase que exige algo que no se dio antes?
- ¿el ejemplo minimo es real o de juguete?
- ¿el intento ingenuo esta desarrollado en serio o es un monigote?
- ¿la seccion 10 describe errores que la gente comete de verdad?
- ¿se cumple lo prometido en el contrato de la seccion 1?
- convencion frente a contenido en la seccion 4: ¿lo distingue de verdad?

**Regla:** nunca gastes un juez en lo que un regex hace mejor.

---

## 4. El juez

### Uno por dimension, no uno global

Un juez que puntua "calidad" da ruido correlacionado consigo mismo. Tres con
lente distinta discrepan, y la discrepancia es la senal:

- **rigor**: handwaving, pasos que faltan, convencion vs contenido
- **pendiente**: escalones, orden de dependencias, contrato cumplido
- **honestidad**: simplificaciones sin declarar, ejercicios usados como
  vertedero de lo dificil, fronteras calladas

### Devuelve findings, no notas

```python
class Finding(BaseModel):
    seccion: int
    cita: str            # texto exacto del capitulo, para poder localizarlo
    regla: str           # que regla del molde rompe
    por_que: str
    que_falta: str       # accionable: que habria que anadir o cambiar
    gravedad: Literal["critico", "serio", "menor"]
```

Una nota no se puede accionar. Una cita si.

### Lo que el juez NO puede ver

El prompt del generador. Si le ensenas el molde entero, valida que se siguio el
formato en lugar de si el capitulo ensena. Al juez se le dan las reglas de SU
dimension y nada mas.

### Ancla la escala con ejemplos reales

Sin ancla todos los jueces convergen al 7. En el prompt del juez van dos
fragmentos: uno de Morin ("esto es un 5") y uno de `2_Dinamica.pdf` ("esto es
un 2"). Ambos sobre el MISMO tema, que es lo que hace la comparacion honesta.

### Calibrar al juez ANTES de generar nada

Sin esto el juez es un generador de numeros bonitos. Banco de pruebas gratis:

| Fuente | Nota esperada |
|---|---|
| Morin, leyes de Newton | alta |
| Griffiths / Hammack (prefacios en ~/Downloads) | alta |
| `2_Dinamica.pdf` (apuntes de asignatura) | baja |
| un capitulo generado a proposito con handwaving | baja |

Si el juez no ORDENA bien esos cinco, no vale, y todo lo que se construya
encima es teatro. Se mide correlacion de orden, no acuerdo exacto de nota.

---

## 5. El grafo (LangGraph)

### Estado

```python
from typing import Annotated, TypedDict
import operator

class Estado(TypedDict):
    tema: str
    nivel: str                       # novato | intermedio | avanzado
    fuentes: list[str]
    contrato: Contrato | None        # el plan; se valida antes de escribir
    bloques: Annotated[dict, merge_bloques]   # reducer: fan-in sin pisarse
    findings: Annotated[list[Finding], operator.add]
    iteracion: int
    historial: list[float]           # score por iteracion
    mejor: dict | None               # NO el ultimo: el mejor
```

Los dos `Annotated` son lo que permite el fan-out. Sin reducer, dos jueces en
paralelo escribiendo `findings` se sobrescriben.

### Bloques de escritura

No una seccion por llamada: grupos que comparten dependencia.

| Bloque | Secciones | Depende de |
|---|---|---|
| A | 2, 3 (problema, intento ingenuo) | contrato. Se escribe SIN usar el vocabulario nuevo |
| B | 4, 5 (definicion, mecanismo) | contrato, A |
| C | 6, 7, 8 (ejemplos, construccion) | B |
| D | 9, 10 (fronteras, como falla) | B, C |
| E | 11 (ejercicios) | todo |
| F | 1, 12 (contrato final, repaso) | todo. Se escriben al final leyendo el resto |

La seccion 1 se redacta al final aunque el contrato se fije al principio: el
plan es un dato desde el minuto cero, su prosa se escribe cuando ya se sabe
que salio.

### Nodos

```python
g = StateGraph(Estado)

g.add_node("investigar", investigar)        # opcional: fuentes reales
g.add_node("contrato", redactar_contrato)   # -> Contrato estructurado
g.add_node("validar", validar_contrato)     # DAG + orden topologico, sin LLM
g.add_node("escribir", escribir_bloque)     # se instancia N veces via Send
g.add_node("lint", lint)                    # capas 1 y 2, sin LLM
g.add_node("juez", juzgar)                  # se instancia 3 veces via Send
g.add_node("agregar", agregar)
g.add_node("refinar", refinar_bloque)
g.add_node("ensamblar", ensamblar)

g.add_edge(START, "investigar")
g.add_edge("investigar", "contrato")
g.add_edge("contrato", "validar")
g.add_conditional_edges("validar", contrato_ok, {
    "rehacer": "contrato",      # max 2 intentos
    "seguir": "escribir",       # via Send, uno por bloque
})
g.add_edge("escribir", "lint")
g.add_conditional_edges("lint", lanzar_jueces)   # Send x3
g.add_edge("juez", "agregar")
g.add_conditional_edges("agregar", decidir, {
    "refinar": "refinar",       # Send SOLO a los bloques con findings
    "listo": "ensamblar",
})
g.add_edge("refinar", "lint")
g.add_edge("ensamblar", END)
```

### Fan-out con Send

```python
def lanzar_jueces(estado: Estado):
    texto = ensamblar_borrador(estado["bloques"])
    return [
        Send("juez", {"dimension": d, "texto": texto, "contrato": estado["contrato"]})
        for d in ("rigor", "pendiente", "honestidad")
    ]
```

Lo mismo para escribir los bloques (respetando el orden de dependencias: A y B
son secuenciales, C/D/E pueden ir en paralelo una vez existe B).

### El loop: refina bloques, no el documento

```python
def decidir(estado: Estado) -> list[Send] | str:
    criticos = [f for f in estado["findings"] if f.gravedad == "critico"]
    score = puntuar(estado["findings"])
    historial = estado["historial"] + [score]

    if not criticos:
        return "listo"
    if estado["iteracion"] >= MAX_ITER:
        return "listo"                       # se ensambla el MEJOR guardado
    if len(historial) >= 2 and score <= historial[-2]:
        return "listo"                       # no mejora: parar, no insistir

    tocados = {f.seccion for f in criticos}
    return [Send("refinar", {"bloque": b, "findings": fs})
            for b, fs in agrupar_por_bloque(criticos, tocados).items()]
```

Regenerar 15 paginas para arreglar la seccion 10 es caro y rompe lo bueno.

### Dos cosas que no son opcionales

**Checkpointer.** Un manual son 30-50 llamadas largas. Sin poder reanudar,
cada corte cuesta el manual entero.

```python
from langgraph.checkpoint.sqlite import SqliteSaver
app = g.compile(checkpointer=SqliteSaver.from_conn_string("manuales.db"))
```

**Interrupt tras el contrato.** Es el equivalente al dialogo del MCP: revisas
el plan antes de gastar en seis bloques. Es donde mas barato sale corregir.

```python
def validar_contrato(estado):
    errores = comprobar_dag(estado["contrato"].inventario)
    if errores:
        return {"findings": errores}
    revisado = interrupt({"contrato": estado["contrato"]})   # tu decides
    return {"contrato": revisado}
```

---

## 6. Salida en disco

```
manuales/<slug>/
  contrato.json          el plan, validado
  fuentes.md
  bloques/A-problema.md ...
  lint.json              findings por iteracion
  historial.json         score por iteracion, para ver si el loop sirve
  manual-<slug>.md       el ensamblado
  manual-<slug>.pdf      cuando se anada el render
```

---

## 7. Orden de construccion

No empezar por el grafo. Empezar por lo que puede invalidarlo todo:

1. **El linter determinista** (capas 1 y 2). Sin LLM, sin LangGraph. Pasale los
   PDFs del USB convertidos a texto y mira que encuentra. Si el linter no
   distingue Morin de los apuntes, las reglas estan mal escritas.
2. **Calibrar el juez** contra esos mismos cinco textos. Si no los ordena, no
   sigas.
3. **Un solo bloque de punta a punta**: contrato → escribir B → lint → juez →
   refinar. Sin grafo todavia, en un script.
4. **Entonces** el grafo, que es solo pegamento.

El paso 1 y el 2 son los que deciden si el sistema funciona. El grafo no.

---

## 8. Cosas a verificar antes de escribir codigo

- La API de LangGraph se mueve. Confirmar contra la documentacion actual
  `Send`, `interrupt`, y el import del checkpointer de sqlite.
- Coste real por manual: medir con UN capitulo antes de lanzar seis.
- Los PDFs del USB hay que pasarlos a texto para el linter y el calibrado.
