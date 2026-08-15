"""Servidor MCP 'profesor'.

QUE HACE   : entrega a Claude un andamiaje pedagogico para que explique cualquier tema.
COMO       : expone 1 tool (la llama Claude) y 1 prompt (la invocas tu con /profesor).
TRANSPORTE : stdio. Claude Code lanza este archivo como subproceso y habla por stdin/stdout.
"""

# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  MAPA DEL ARCHIVO                                                         ║
# ╠═══════════════════════════════════════════════════════════════════════════╣
# ║  ZONA 1  IMPORTS    traer herramientas de fuera                           ║
# ║  ZONA 2  SERVIDOR   identidad del servidor + log()                        ║
# ║  ZONA 3  MOLDES     los textos completos, con huecos {asi}                ║
# ║  ZONA 4  DATOS      los fragmentos que rellenan los huecos                ║
# ║  ZONA 4.5 FORMULARIOS  la forma de las preguntas del dialogo              ║
# ║  ZONA 5  TOOL       la llama CLAUDE. Abre el dialogo. async.              ║
# ║  ZONA 6  PROMPT     lo llamas TU. Verboso, sin dialogo.                   ║
# ║  ZONA 7  ARRANQUE   pone el servidor a escuchar                           ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
#
# ┌───────────────────────────────────────────────────────────────────────────┐
# │  DOS PUERTAS DE ENTRADA, DOS COMPORTAMIENTOS                              │
# ├───────────────────────────────────────────────────────────────────────────┤
# │  TOOL   (ZONA 5)  la llama Claude    -> SIEMPRE abre el dialogo           │
# │  PROMPT (ZONA 6)  la llamas tu con / -> verbosa, argumentos escritos      │
# │                                                                           │
# │  No es un capricho: la elicitacion SOLO existe durante la ejecucion de    │
# │  una tool. Un prompt no puede abrir dialogos aunque quisieramos.          │
# └───────────────────────────────────────────────────────────────────────────┘
#
# ┌───────────────────────────────────────────────────────────────────────────┐
# │  LA DIFERENCIA ENTRE ZONA 3 Y ZONA 4                                      │
# ├───────────────────────────────────────────────────────────────────────────┤
# │  ZONA 3 = MOLDES.     Textos completos. Se ELIGE uno.                     │
# │  ZONA 4 = FRAGMENTOS. Trozos sueltos. RELLENAN los huecos del elegido.    │
# │                                                                           │
# │  Distinto trabajo -> distinta zona. Nunca se anidan una dentro de otra.   │
# └───────────────────────────────────────────────────────────────────────────┘
#
# ┌───────────────────────────────────────────────────────────────────────────┐
# │  RECETA A: "quiero anadir un METODO nuevo"   (como Cornell o Feynman)     │
# ├───────────────────────────────────────────────────────────────────────────┤
# │    1) ZONA 3  ->  variable MOLDE_LOQUESEA con el texto                    │
# │    2) ZONA 3  ->  una entrada mas en el diccionario MODOS                 │
# │    3) ZONA 5  ->  el valor nuevo dentro del Literal de 'modo'             │
# │    4) ZONA 6  ->  igual                                                   │
# │  El cuerpo de las funciones NO se toca. Ese es el premio del diseno.      │
# └───────────────────────────────────────────────────────────────────────────┘
#
# ┌───────────────────────────────────────────────────────────────────────────┐
# │  RECETA B: "quiero anadir un EJE nuevo"   (como hiciste con 'tono')       │
# ├───────────────────────────────────────────────────────────────────────────┤
# │    1) ZONA 4  ->  un diccionario nuevo con los fragmentos                 │
# │    2) ZONA 3  ->  un hueco {ajuste_X} DENTRO de los moldes que lo usen    │
# │    3) ZONA 5  ->  firma + docstring + .get() + .format()                  │
# │    4) ZONA 6  ->  igual                                                   │
# └───────────────────────────────────────────────────────────────────────────┘
#
# ┌───────────────────────────────────────────────────────────────────────────┐
# │  OTRAS RECETAS                                                            │
# ├───────────────────────────────────────────────────────────────────────────┤
# │  cambiar el TEXTO de un metodo    ->  solo ZONA 3                         │
# │  cambiar el TEXTO de un nivel     ->  solo ZONA 4                         │
# │  cambiar CUANDO se dispara        ->  solo el docstring (ZONA 5)          │
# └───────────────────────────────────────────────────────────────────────────┘


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  ZONA 1 — IMPORTS                                                         ║
# ║  Que vive aqui : herramientas que vienen de fuera de este archivo.        ║
# ║  Tocas esto si : necesitas algo nuevo del lenguaje o del SDK.             ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

# sys      : PYTHON. Solo lo usamos para escribir en stderr. Nunca en stdout.
import sys

# Literal  : PYTHON (modulo typing). Es un SELECTOR: cierra un parametro a una
#            lista de valores exactos. El SDK lo traduce a "enum" en el schema.
from typing import Literal

# BaseModel: PYDANTIC. Es la libreria que YA estaba validando tus parametros por
#            debajo (la que rechazaba tono='aleman'). Hasta ahora no la tocabas.
#            Ahora la usas a mano para describir el FORMULARIO del dialogo.
# Field    : PYDANTIC. Anade descripcion y valor por defecto a un campo.
#            La descripcion es la etiqueta que ve el humano en el dialogo.
from pydantic import BaseModel, Field

# MCPServer: SDK. La clase principal. En el SDK v1 se llamaba FastMCP.
# Context  : SDK. El canal de vuelta hacia el cliente DURANTE la ejecucion.
#            Con el puedes preguntar (elicit), avisar (log), o reportar progreso.
#            Hasta ahora tus tools solo devolvian texto y se acababa ahi.
from mcp.server.mcpserver import Context, MCPServer


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  ZONA 2 — EL SERVIDOR                                                     ║
# ║  Que vive aqui : la identidad del servidor y la funcion de depuracion.    ║
# ║  Tocas esto si : cambias el nombre, la version, o como orientas a Claude. ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

mcp = MCPServer(
    name="profesor",
    title="Profesor",
    version="0.1.0",
    instructions=(
        "Servidor que impone una prosa explicativa, clara y directa. "
        "Usa la tool 'explicar' cuando el usuario pida entender un tema, "
        "no solo resolverlo."
    ),
)


def log(mensaje: str) -> None:
    """QUE HACE : imprime para depurar.

    COMO     : escribe en stderr, que NO es el canal del protocolo.
    FALLA SI : usas print() en su lugar. print() va a stdout, corrompe el JSON
               del protocolo, y Claude Code desconecta el servidor sin explicacion.
    """
    print(mensaje, file=sys.stderr, flush=True)


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  ZONA 3 — LOS MOLDES                                                      ║
# ║  Que vive aqui : un string completo por cada metodo, y el selector MODOS. ║
# ║  Tocas esto si : cambias la estructura de un metodo, o anades uno nuevo.  ║
# ╠═══════════════════════════════════════════════════════════════════════════╣
# ║  REGLA DE ORO: un {hueco} SOLO existe DENTRO de las comillas de un molde. ║
# ║                                                                           ║
# ║  METODOS ABIERTOS  : tienen huecos de nivel y/o tono -> se modulan.       ║
# ║  METODOS CERRADOS  : no tienen nivel ni tono. El metodo dicta su forma.   ║
# ║                                                                           ║
# ║  Abierto no es un interruptor, es una lista de ejes: 'clasico' abre nivel ║
# ║  y tono, 'manual' abre solo nivel. Cada molde declara sus huecos arriba,  ║
# ║  y la cascada de la ZONA 5 pregunta esos y nada mas.                      ║
# ║                                                                           ║
# ║  LAS EXCEPCIONES: dos huecos los llevan TODOS los moldes, abiertos y      ║
# ║  cerrados, porque no dicen nada sobre el metodo:                          ║
# ║    {ajuste_extension}  cuanto texto ocupa ejecutarlo. Un Cornell corto    ║
# ║                        sigue siendo un Cornell; sin tono no seria nada.   ║
# ║    {marcado}           como se marca el texto, no que se dice en el.      ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

# ── MOLDE 1: CLASICO (abierto) ────────────────────────────────────────────────
#    Huecos: {tema} {ajuste_nivel} {ajuste_tono} {ajuste_extension} {marcado}
MOLDE_CLASICO = """\
Explica **{tema}** siguiendo exactamente esta estructura, sin saltarte pasos:

1. **Qué es** — Una sola frase, directa, exponiendo el concepto y las partes que
   lo conforman. Sin rodeos, sin "es un concepto que...".
2. **El modelo mental** — Una analogía concreta con algo que ya se conoce.
   Di explícitamente en qué punto la analogía deja de funcionar.
3. **El mecanismo** — Cómo funciona por dentro, paso a paso, en orden causal
   y secuencial. Cada paso debe responder "y entonces qué pasa".
4. **Ejemplo mínimo** — El caso más pequeño posible que aún sea real.
   Nada de `foo`/`bar` si el tema admite un ejemplo del mundo real.
5. **Cómo falla** — Los 2 o 3 errores que comete todo el mundo la primera vez,
   y qué síntoma produce cada uno. Esto es lo más valioso: dilo con detalle.
6. **Comprobación** — Una pregunta que solo se puede responder si se entendió
   el mecanismo. No de memoria: de razonamiento.

Reglas de prosa que aplican a toda la respuesta:
- Frases cortas. Una idea por frase.
- Voz activa. "El servidor envía", no "es enviado por el servidor".
- Cero relleno: nada de "es importante notar que", "cabe destacar", "en resumen".
- Si usas un término técnico, defínelo en el momento, entre guiones.
- No pidas permiso para continuar ni ofrezcas "¿quieres que profundice?".
  Da la explicación completa de una vez.

{ajuste_nivel}

{ajuste_tono}

{ajuste_extension}

{marcado}
"""

# ── MOLDE 2: CORNELL (cerrado) ────────────────────────────────────────────────
#    Huecos: {tema}  {ajuste_extension}  {marcado}
MOLDE_CORNELL = """\
Explica **{tema}** con el método Cornell. Divide la respuesta en tres bloques,
en este orden y con estos títulos exactos:

**NOTAS**
El desarrollo del tema. Ideas sueltas pero explicadas en su esencia no se puede explicar de forma circular, cada una en su línea, sin párrafos largos.
Frases telegráficas: son notas, no prosa. Quédate con los detalles que sostienen
cada idea, no con los que la adornan.

**CLAVES**
Preguntas y palabras clave que interrogan las notas de arriba. Cada entrada
apunta a una nota concreta. Escribe preguntas que obliguen a recuperar la nota
de memoria, no a reconocerla: "¿por qué X provoca Y?" en vez de "¿qué es X?" finalmente añade la respuesta debajo de cada pregunta.

**RESUMEN**
Tres o cuatro frases escritas para alguien que NO ha leído las notas. Si el
resumen necesita las notas para entenderse, está mal escrito. Reescríbelo.

Reglas: frases cortas, voz activa, cero relleno. Define cada término técnico
la primera vez que aparezca.

{ajuste_extension}

{marcado}
"""

# ── MOLDE 3: FEYNMAN (cerrado) ────────────────────────────────────────────────
#    Huecos: {tema}  {ajuste_extension}  {marcado}
MOLDE_FEYNMAN = """\
Explica **{tema}** con el método Feynman. Cuatro pasos, en este orden y con
estos títulos exactos:

**1. EXPLICACIÓN LLANA**
Explica el tema como se lo explicarías a alguien de doce años en el sentido de la simplicidad lexica y la comprensión directa. Cero jerga.
Si necesitas una palabra técnica, no la uses todavía: rodéala creando una expresion ad-hoc. Vocabulario
cotidiano y frases cortas. No te pases con el uso de metaforas, no crees una explicacion minima o mediocre para completarla en la parte 2 sino que haz una funcional

**2. DÓNDE SE ROMPE**
Ahora completa puntos en profundidad que no se han dicho antes por brevedad o simplificación.

Señala los puntos concretos donde la explicación llana se queda corta: dónde
simplificaste de más, o dónde hace falta sí o sí un término técnico. Nombra
ahora esos términos y define cada uno en una frase. Este paso ES el método:
el hueco de la explicación es el hueco de la comprensión.

**3. ANALOGÍA Y RECONSTRUCCIÓN**
Esta es la unica parte donde brillan las metaforas perse
Coge cada punto del paso 2 y explícalo con una analogía concreta y cotidiana.
Di explícitamente en qué punto cada analogía deja de funcionar — una analogía
sin límite declarado enseña mal.

**4. PRUEBA DE SIMPLICIDAD**
Reescribe todo el tema en tres frases, sin jerga y sin analogías. Si no cabe
en tres frases, no está entendido: vuelve al paso 2 y busca qué falta.

Reglas: frases cortas, voz activa, cero relleno.

{ajuste_extension}

{marcado}
"""

# ── MOLDE 4: MANUAL (abierto a medias: consume nivel, NO tono) ────────────────
#    El molde impone la prosa entera (doce secciones y sus reglas de escritura),
#    asi que el tono no tiene donde entrar: elegirlo no cambiaria una coma.
#    Pero el nivel SI, y ademas es obligatorio: la seccion 1 es un contrato de
#    entrada, y un contrato sin audiencia declarada no se puede escribir.
#    Por eso la cascada de la ZONA 5 le pregunta nivel, y solo nivel.
#    De donde sale el metodo: metodo_manual.py, en la raiz del repo.
#    Huecos: {tema} {ajuste_nivel} {ajuste_extension} {marcado}
MOLDE_MANUAL = """\
Explica **{tema}** como lo haria un capitulo de un libro de texto de los que se
citan por lo bien que explican, no por famosos. No es un resumen ni una entrada
de enciclopedia: es una unidad de estudio completa, y el lector termina sabiendo
hacer algo que antes no sabia.

Doce secciones, en este orden, con estos titulos exactos. No se salta ninguna.
Si una no aplica al tema, escribe el titulo y una linea diciendo por que no
aplica: el hueco declarado informa, el hueco silencioso engana.

**1. CONTRATO**
Tres cosas, en tres bloques cortos:
- *Que se presupone*: lista concreta de lo que hay que saber ya. Nada de "unos
  conocimientos basicos". Nombra los conceptos exactos, y para cada uno una
  frase que permita comprobar si se tienen ("deberias poder decir que hace X
  sin mirarlo").
- *Que NO se presupone*: lo que suele darse por sabido en otros textos y aqui
  se va a explicar igualmente. Esta linea es la que baja la barrera de entrada.
- *Vocabulario que se va a introducir*: la lista, EN ORDEN, de los terminos
  nuevos que el capitulo define, cada uno con la seccion donde se define. Es el
  indice lexico del capitulo y se escribe antes de redactarlo, porque fija el
  orden de todo lo demas: si un termino de la lista necesita otro que aparece
  mas abajo, el orden esta mal y hay que rehacerlo aqui, no parchearlo luego.
  Los terminos que vienen del bloque "que se presupone" NO entran en esta lista:
  esos se usan directamente, y esa es justo la diferencia entre prestar un
  concepto y contraerlo.
- *Que sabras hacer al terminar*: en verbos de accion y comprobables. "Sabras
  derivar Y a partir de Z", no "entenderas Y".
- *Que forma tiene la dificultad*: una o dos frases diciendo por que este tema
  cuesta, y de que tipo es el coste: muchas piezas pequenas mal conectadas, o
  pocas piezas pero muy abstractas, o una sola idea contraintuitiva, o
  simplemente mucha notacion nueva. No vale "es un tema dificil". El lector que
  sabe que forma tiene la cuesta no confunde la cuesta con su propia torpeza, y
  sabe si su atasco es normal o es que se perdio algo.
- *Ruta de lectura*: si alguna seccion se puede saltar en una primera lectura,
  dilo aqui y di el coste exacto de saltarla y donde habria que volver. Un
  capitulo del que no se dice que es opcional es un capitulo obligatorio.

**2. EL PROBLEMA QUE LO HIZO NACER**
Antes de cualquier definicion. Que pregunta no se sabia responder, o que cosa
se rompia, antes de que esto existiera. Si hay una historia real (quien se topo
con ello y cuando), cuentala en cuatro o cinco frases: el contexto no es adorno,
es lo que hace que la definicion parezca inevitable en vez de arbitraria.
Cierra con la pregunta concreta que el resto del capitulo responde.
Esta seccion va ANTES de la definicion, asi que se escribe entera en lenguaje
llano: describe la cosa por lo que hace y por el agujero que tapa, sin usar
todavia el termino tecnico ni ninguno de los del inventario. Si te sale usarlo,
es que estas definiendo aqui, y aqui no toca.

**3. EL INTENTO INGENUO**
La solucion que se le ocurre a cualquiera al oir el problema. Desarrollala en
serio, no como un monigote: tiene que ser lo bastante buena como para que se
entienda por que alguien la intentaria. Despues, rompela con un caso concreto,
con numeros o con un ejemplo real. Lo que sobrevive de ese naufragio es
exactamente lo que la definicion de la seccion siguiente tiene que capturar.

**4. LA DEFINICION, Y POR QUE ESTA Y NO OTRA**
Ahora si: el enunciado preciso. Cada termino nuevo definido en el momento, y
dicho ademas como se lee en voz alta si lleva notacion.
Separa lo que es CONVENCION de lo que es AFIRMACION CON CONTENIDO. De todo lo
que acabas de enunciar, di que parte es una definicion disfrazada de ley (podria
haberse elegido de otro modo y no se descubre, se acuerda) y que parte dice algo
del mundo que podria ser falso. Si dos definiciones se sostienen mutuamente,
senalalo en vez de taparlo, y localiza despues donde esta el contenido de verdad.
El lector que no distingue convencion de contenido cree que no entiende cuando lo
que pasa es que no hay nada que entender en esa linea.

Aqui es donde el termino recibe su nombre por primera vez. Nombrarlo no es
definirlo: si lo unico que hace la frase es asignar una etiqueta ("a esto se le
llama X"), falta la definicion. Y ninguna definicion puede apoyarse en un
termino que aun no exista ni en si misma: si al escribirla necesitas otro
concepto del inventario que va mas abajo, el orden esta mal.
Luego lo que casi ningun texto hace y es lo que distingue a los buenos: por que
se eligieron ESTOS primitivos. Que definicion alternativa se descarto y que se
pierde con ella. Si el objeto de partida hubiera sido otro, di como habria
cambiado todo lo que viene despues.
La notacion se introduce cuando hace falta, nunca antes, y se justifica.

**5. EL MECANISMO, PASO A PASO**
El desarrollo central: la derivacion, la demostracion o el funcionamiento
interno, completo y en orden causal. Cada paso responde "y entonces que pasa" y
enlaza con el anterior sin salto.
Esta prohibido: "se puede demostrar que", "es facil ver que", "obviamente",
"se deja como ejercicio", "por analogia con lo anterior". Si un paso es largo,
se escribe largo. Si de verdad hay que saltarselo, se dice exactamente que se
esta saltando, por que, y donde esta hecho entero.
Cuando un paso sea el dificil de verdad, anuncialo antes ("este es el paso que
cuesta") y desmenuzalo mas que los demas. Ahi es donde se pierde la gente.

**6. EL EJEMPLO MINIMO, TRABAJADO ENTERO**
El caso mas pequeno que sigue siendo real. Numeros concretos, datos concretos,
nada de foo ni bar si el tema admite algo del mundo. Se resuelve delante del
lector, sin saltarse la aritmetica ni los pasos intermedios, y comentando en
cada paso que parte del mecanismo de la seccion 5 se esta usando.

**7. EL EJEMPLO QUE YA DUELE**
Un segundo caso, esta vez con la complicacion que el minimo no tenia: el que
tiene ruido, un caso limite, una excepcion o una escala mayor. Aqui se ve si el
mecanismo se entendio o solo se copio. Resuelvelo igual de completo, y senala
en que momento exacto este caso obliga a hacer algo que el minimo no pedia.

**8. CONSTRUCCION**
Si el tema admite construir algo (un programa, una demostracion propia, un
montaje, un calculo, un argumento), se construye aqui pieza a pieza hasta que
funcione. Es el patron de los libros del corpus que mas se recomiendan por
explicativos: se llega a una cosa que existe y se puede tocar.
Si el tema no admite construccion, sustituye esta seccion por una
RECONSTRUCCION: rehacer el razonamiento central desde cero, con otras palabras
y en otro orden, para que se vea que no dependia de como se conto la primera vez.

**9. FRONTERAS**
Donde deja de valer lo dicho. Tres bloques:
- *Que he simplificado*: cada simplificacion del capitulo, nombrada, y que
  version completa le corresponde.
- *Donde el modelo se rompe*: los casos fuera de rango, y que pasa si se aplica
  igualmente.
- *Que renuncia asume este capitulo*: rigor a cambio de claridad, generalidad a
  cambio de concrecion, o al reves. Se declara. Una renuncia declarada es
  honesta; la misma renuncia callada es un error de bulto.

**10. COMO FALLA LA GENTE**
Los tres o cuatro errores que comete casi todo el mundo la primera vez. Para
cada uno: en que consiste, que sintoma produce (que resultado raro, que mensaje,
que contradiccion), por que es tan tentador caer en el, y como se corrige.
Esta seccion se escribe con detalle: es la que mas ensena de todo el capitulo,
porque es la unica que habla de lo que le va a pasar al lector de verdad.

**11. EJERCICIOS**
Tres tramos, con dificultad en pendiente continua, sin escalones:
- *Mecanicos* (2 o 3): aplicar el procedimiento tal cual. Sirven para coger
  soltura, no para pensar.
- *De comprension* (2 o 3): obligan a reconstruir el argumento, no a repetirlo.
  Del tipo "por que falla si cambio X", "que parte del mecanismo se rompe si Y".
- *Duro* (1): el que se resiste, el que puede llevar un rato largo. Que sea
  resoluble con lo del capitulo y nada mas.
Cada ejercicio lleva debajo su respuesta, y la respuesta explica el camino, no
solo el resultado: como se le ocurre a uno ese camino. Si un ejercicio se
resuelve con un truco, di de donde sale el truco.
Y la regla que separa el ejercicio honesto del vertedero: un ejercicio nunca es
la manera de sacar del texto algo dificil que tocaba explicar. Si un paso del
mecanismo es duro, va en la seccion 5, desarrollado. Puedes dejarle al lector
una parte del razonamiento, pero solo diciendo que se la dejas y por que le
conviene hacerla el, nunca en silencio ni para ahorrarte el trabajo.

**12. LA PAGINA DE REPASO**
Escrita para quien ya leyo el capitulo y vuelve dentro de seis meses, no para
quien aprende. Las definiciones, el resultado central y la advertencia mas
importante, en el minimo de lineas posible. Sin analogias y sin motivacion: eso
ya cumplio su funcion. Si esta pagina se entiende sin haber leido el capitulo,
esta mal escrita: es un resumen, y aqui no se pedia un resumen.

════════════════════════════════════════════════════════════════════════════

Reglas de escritura del manual. Aplican a las doce secciones:

- **Pendiente lineal.** Ninguna frase debe exigir algo que no se haya dado
  antes en el propio texto o declarado en el contrato. Si al releer encuentras
  un escalon, mete el peldano que falta: no bajes el techo.
- **Intuicion antes del formalismo, nunca en su lugar.** Primero por que tiene
  sentido, despues el enunciado exacto. Quedarse en la intuicion es enganar;
  empezar por el formalismo es perder al lector.
- **Cero handwaving.** Ver la seccion 5. Es la regla que mas se incumple.
- **Conversacional y preciso a la vez.** Se puede escribir como quien habla y
  seguir siendo exacto: la prosa es llana, pero cada palabra esta puesta a
  proposito y ninguna sobra. El lector deberia poder leerlo del tiron y a la vez
  tener que leer cada palabra.
- **Handholding calibrado.** Acompanar sin infantilizar. Ni "no te preocupes,
  esto es muy facil" ni dar por hecho el salto dificil. El termometro es el
  contrato de la seccion 1.
- **Una idea por frase, voz activa, cero relleno.** Nada de "es importante
  destacar", "cabe senalar", "como hemos visto". Si algo es importante, se nota
  porque esta desarrollado, no porque se anuncie.
- **Ningun concepto se usa antes de existir.** Es la regla de orden, y manda
  sobre el resto:
  · El capitulo se ordena por dependencias del que aun no sabe, no por la
    logica del que ya sabe. Cada termino aparece despues de todo lo que hace
    falta para entenderlo.
  · Los terminos tecnicos se definen la primera vez, en el momento y en linea.
    Nunca "ya lo veremos mas adelante" para algo que se acaba de usar.
  · Nada de definiciones circulares, ni directas ni en cadena: si A se apoya en
    B y B se apoya en A, el par entero esta sin definir por mucho que suene bien.
  · Nombrar no es definir. Una etiqueta sin contenido ("a esto se le llama X")
    deja el concepto vacio y ademas lo disfraza de sabido.
  · Si un concepto hace falta antes de su turno, tienes dos salidas legitimas y
    ninguna mas: decirlo en lenguaje llano sin nombrarlo, o adelantar su
    definicion completa. Lo prohibido es la tercera, usar el nombre a credito.
  · Al terminar, recorre el capitulo con el inventario de la seccion 1 en la
    mano y comprueba termino por termino que ninguno aparece antes de su
    definicion. Ese repaso es parte del metodo, no un extra.
- **Ningun apartado se anuncia ni se pide permiso.** Nada de "¿quieres que
  profundice?". El capitulo se entrega entero.

════════════════════════════════════════════════════════════════════════════

Notacion, formulas y figuras. El capitulo se escribe en Markdown y puede acabar
impreso, asi que la notacion se escribe pensando en pagina, no en pantalla:

- **Formulas en linea o en bloque.** En linea con $...$ lo que va dentro de una
  frase y se lee seguido. En bloque con $$...$$ lo que se razona: una
  derivacion, un resultado central, cualquier cosa sobre la que se vuelva.
- **Numera solo lo que vuelvas a nombrar.** Toda formula en bloque que se cite
  despues lleva numero de seccion y orden: (4.1), (4.2), (5.1). Las que no se
  citan no se numeran. El numero es la promesa de que esa formula se va a usar
  otra vez, y una numeracion que lo numera todo no dice nada.
- **Refiere por numero, nunca por posicion.** "Por (4.1)", no "por la formula de
  arriba" ni "la anterior". En pagina impresa "arriba" puede caer dos paginas
  atras, y en pantalla depende del ancho.
- **Ninguna formula suelta.** Antes de cada una, una linea diciendo que va a
  decir. Despues, que es cada simbolo. Y la primera vez que aparece un simbolo
  nuevo, como se lee en voz alta: quien no sabe pronunciar $\\partial f/\\partial x$
  no puede pensar con ello.
- **Declara la convencion tipografica** la primera vez que la uses, en una
  linea: que va en negrita, que en cursiva, que letras se reservan para que.
  Una convencion sin declarar obliga al lector a inferirla de los ejemplos.
- **Una cadena de igualdades es una sola formula**, alineada por el signo igual
  y con un unico numero al final. No se trocea en tres formulas numeradas.

- **Un diagrama se gana el sitio** cuando ensena una relacion que la prosa
  necesitaria mas de tres frases para describir: una estructura, un flujo
  causal, una jerarquia, una geometria, una particion de casos. Nunca para
  ilustrar algo que ya quedo dicho. Un capitulo denso puede no llevar ninguno,
  y eso esta bien; lo que no vale es el diagrama de adorno.
- **Formato**: un bloque ```mermaid cuando la figura sea de cajas, flechas,
  arboles o estados. Si lo que hace falta es una grafica de una funcion o una
  geometria con medidas, describela con precision suficiente para dibujarla
  (ejes, escalas, que se marca en cada punto) en vez de fingirla con ASCII.
- **Cada figura lleva numero y pie**: "Figura 5.1: ...". El pie dice QUE HAY QUE
  MIRAR, no repite el titulo de la seccion.
- **Cada figura se referencia desde el texto** por su numero. Una figura que la
  prosa no menciona es decoracion, y se quita.
- **Donde suelen ganarselo**: la seccion 3 (por que revienta el intento
  ingenuo), la 5 (el mecanismo en orden causal) y la 9 (donde esta el borde del
  modelo). Si el tema es visual o espacial y el capitulo sale sin una sola
  figura, faltan.

{ajuste_nivel}

{ajuste_extension}

{marcado}
"""

# ── MOLDE 5: LIBRE (la puerta de salida) ──────────────────────────────────────
#    Huecos: {tema}  {ajuste_extension}  {marcado}
#
#    POR QUE EXISTE: sin esto, la unica forma de decir "esta vez no" era quitar
#    el servidor entero. Global, permanente y con reinicio, para una respuesta.
#    Aqui la renuncia vale una linea del desplegable.
#
#    OJO A LO QUE NO LLEVA: ni nivel, ni tono, ni reglas de prosa. Si le
#    colaramos "frases cortas, voz activa" seguirias dentro del andamiaje,
#    solo que con menos pasos. Elegir 'libre' tiene que devolverte a Claude
#    tal cual, o no es una salida: es otro molde mas disfrazado.
MOLDE_LIBRE = """\
Explica **{tema}** sin andamiaje.

No apliques ningún método fijo. Sin apartados obligatorios, sin analogía de
oficio, sin pregunta de comprobación al final. Elige tú la forma que mejor le
venga al tema y responde como responderías si nadie te hubiera dado un guion.

{ajuste_extension}

{marcado}
"""

# ── EL SELECTOR ───────────────────────────────────────────────────────────────
# QUE HACE : mapea el nombre de un metodo a su molde.
# OJO      : las claves deben coincidir LETRA POR LETRA con el Literal de la
#            ZONA 5. Si el Literal dice "clasico" y aqui pusieras "CLASICOMCP",
#            .get() no encontraria la clave y caeria al valor por defecto.
#            Sin error. Sin aviso. Siempre el mismo molde. Ese es el peligro.
MODOS = {
    "clasico": MOLDE_CLASICO,
    "cornell": MOLDE_CORNELL,
    "feynman": MOLDE_FEYNMAN,
    "manual": MOLDE_MANUAL,
    "libre": MOLDE_LIBRE,
}


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  ZONA 4 — LOS DATOS                                                       ║
# ║  Que vive aqui : un diccionario por cada EJE. Clave -> fragmento.         ║
# ║  Tocas esto si : cambias el texto de una opcion o anades una opcion.      ║
# ╠═══════════════════════════════════════════════════════════════════════════╣
# ║  Estos NO son moldes: son trozos que se meten en el hueco de un molde.    ║
# ║  Viven al mismo nivel que MODOS, no dentro. Son dos cosas paralelas.      ║
# ║                                                                           ║
# ║  NIVEL y TONO solo los consume el molde CLASICO. Los cerrados los         ║
# ║  ignoran, y eso se resuelve solo: format ignora lo que sobra. Sin ifs.    ║
# ║  EXTENSION la consumen los tres. Ver la nota de la ZONA 3.                ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

# ── EJE 1: NIVEL ──────────────────────────────────────────────────────────────
NIVELES = {
    "novato": (
        "Nivel NOVATO: asume cero conocimiento previo del área. "
        "Define cada término técnico la primera vez que aparezca. "
        "Prioriza la analogía y el ejemplo por encima del mecanismo interno."
    ),
    "intermedio": (
        "Nivel INTERMEDIO: asume que se conocen los fundamentos del área "
        "pero no este tema concreto. Ve directo al mecanismo. "
        "Compara con conceptos vecinos que ya se dominan."
    ),
    "avanzado": (
        "Nivel AVANZADO: asume dominio del área. Salta la analogía si no aporta. "
        "Céntrate en los casos límite, las decisiones de diseño y el porqué "
        "de que esté hecho así y no de otra forma."
    ),
}

# ── EJE 2: TONO ───────────────────────────────────────────────────────────────
# OJO PYTHON: dos strings pegados se unen SIN espacio.
#             "seco" "Da una"  ->  "secoDa una"
TONO = {
    "formal": (
        "Tono FORMAL: explicación clásica y de libro sobre la materia. "
        "Sin abusar de oraciones subordinadas ni de conectores innecesarios. "
        "Va al grano: directo y seco. Prosa seria y poco relacional."
    ),
    "out of the box": (
        "Tono OUT OF THE BOX: pensamiento lateral sobre el concepto, ajustado "
        "al nivel indicado. Busca las conexiones que no se ven a priori y los "
        "ángulos muertos del tema. Señala qué asunciones da por buenas todo el "
        "mundo sin comprobarlas."
    ),
}

# ── NO ES UN EJE: EL MARCADO ──────────────────────────────────────────────────
# QUE ES  : un fragmento fijo. Rellena un hueco, como los ejes, pero NO tiene
#           diccionario porque no hay nada que elegir. Un eje son opciones; esto
#           es una convencion. Si algun dia quieres poder apagarlo, ahi si
#           tocaria convertirlo en eje (RECETA B) — hoy seria un diccionario de
#           una sola entrada, que es un diccionario de mentira.
#
# POR QUE EXISTE: para que los terminos clave se distingan en el CLI.
#
# LA LECCION QUE ENSENA ESTE FRAGMENTO — y es la de todo el protocolo:
#           un servidor MCP NO pinta nada. Devuelve texto y se acabo. Quien
#           colorea es el cliente, leyendo el marcado. Por eso la regla dice
#           "marca", no "colorea": si aqui escribieramos codigos ANSI a pelo,
#           funcionaria en la terminal y saldria como basura literal en la web
#           y en el IDE. El marcado viaja a todas partes; el color, no.
MARCADO = """\
Marcado del texto:
- Cada término técnico va entre `backticks` la primera vez que aparece, y solo
  la primera. Si lo repites en cada línea deja de destacar nada.
- Si titulas secciones, ponlas en **negrita**.
- No escribas el color a mano: nada de códigos ANSI ni de HTML. Tú marcas,
  el cliente pinta. Lo que en tu terminal sería color, en otro cliente sería
  basura en mitad de la frase.
"""

# ── EJE 3: EXTENSION ──────────────────────────────────────────────────────────
# OJO: este eje lo consumen LOS CUATRO moldes, no solo el clasico. Por eso los
#      fragmentos hablan de "apartados o puntos" y no de pasos concretos:
#      tienen que valer igual para las 6 secciones del clasico, los 3 bloques
#      de Cornell, los 4 pasos de Feynman y la forma libre, que no tiene
#      apartados de ningun tipo.
#
# LA REGLA QUE SOSTIENE ESTE EJE: 'corto' recorta el DESARROLLO, nunca la
#      ESTRUCTURA. Si dejara borrar apartados, el metodo se rompe y ya no
#      estarias eligiendo extension: estarias eligiendo otro metodo distinto.
EXTENSION = {
    "normal": (
        "Extensión NORMAL: desarrolla cada apartado o punto hasta que quede "
        "entendido. Ni alargues por alargar ni recortes el mecanismo o los "
        "fallos, que son lo que de verdad enseña."
    ),
    "corto": (
        "Extensión CORTA: no dejes fuera ningún apartado ni ningún punto que "
        "fueras a cubrir, pero reduce cada uno a su núcleo: tres frases como "
        "máximo. Un solo ejemplo. Una sola analogía. Nada de listas anidadas. "
        "Si algo no cabe en tres frases, sobra texto: no falta espacio."
    ),
}


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  ZONA 4.5 — LOS FORMULARIOS                                               ║
# ║  Que vive aqui : la FORMA de las preguntas que abre el dialogo.           ║
# ║  Tocas esto si : cambias que se pregunta o en que orden.                  ║
# ╠═══════════════════════════════════════════════════════════════════════════╣
# ║  Esto no es un molde ni un fragmento: es una TERCERA cosa.                ║
# ║    molde     -> texto que se elige                                        ║
# ║    fragmento -> texto que rellena un hueco                                ║
# ║    formulario-> la forma de una PREGUNTA al humano                        ║
# ║                                                                           ║
# ║  COMO FUNCIONA: una clase Pydantic. Cada atributo es un campo del         ║
# ║  dialogo. Un Literal se traduce a "enum" -> el cliente lo pinta como      ║
# ║  selector, no como caja de texto. Es la misma traduccion que ya hacian    ║
# ║  tus parametros, aplicada ahora a una pregunta.                           ║
# ║                                                                           ║
# ║  LIMITE DE LA SPEC: solo tipos primitivos (str, int, bool, Literal).      ║
# ║                     Nada de listas ni objetos anidados.                   ║
# ╚═══════════════════════════════════════════════════════════════════════════╝


class EleccionModo(BaseModel):
    """PASO 1 del dialogo: siempre se pregunta esto.

    Van juntos modo y extension porque los dos aplican SIEMPRE, elijas el
    metodo que elijas. Lo que solo vale para 'clasico' vive en el paso 2.
    """

    # QUE HACE : un desplegable con los tres metodos.
    # OJO      : los valores DEBEN coincidir con las claves de MODOS.
    #            Misma trampa de siempre, ahora en un sitio mas.
    modo: Literal["clasico", "cornell", "feynman", "manual", "libre"] = Field(
        default="clasico",
        description="Método de explicación ('libre' = sin andamiaje)",
    )
    # OJO : mismos valores que las claves de EXTENSION.
    extension: Literal["normal", "corto"] = Field(
        default="normal",
        description="Extensión de la explicación",
    )


class AjusteClasico(BaseModel):
    """PASO 2 del dialogo: SOLO si en el paso 1 se eligio 'clasico'.

    Cornell y Feynman son metodos cerrados: preguntarles nivel o tono
    no tendria efecto, asi que ni se pregunta.
    """

    nivel: Literal["novato", "intermedio", "avanzado"] = Field(
        default="intermedio",
        description="Profundidad asumida",
    )
    tono: Literal["formal", "out of the box"] = Field(
        default="formal",
        description="Registro de la prosa",
    )


class AjusteManual(BaseModel):
    """PASO 2 alternativo: SOLO si en el paso 1 se eligio 'manual'.

    Un formulario propio, y no el de 'clasico', por una sola razon: el manual
    no tiene hueco de tono. Si reutilizaramos AjusteClasico, el desplegable
    preguntaria un tono que format tira a la basura sin decir nada. Preguntar
    algo que no cambia la respuesta es peor que no preguntarlo: promete un
    control que no existe.
    """

    nivel: Literal["novato", "intermedio", "avanzado"] = Field(
        default="intermedio",
        description="Para quién se escribe el capítulo (fija el contrato de entrada)",
    )


# QUE HACE : los valores con los que se responde si el humano cancela.
# POR QUE  : cancelar no puede dejar la tool sin datos. Un solo sitio
#            donde estan definidos, para no repetirlos por el codigo.
POR_DEFECTO = {
    "modo": "clasico",
    "nivel": "intermedio",
    "tono": "formal",
    "extension": "normal",
}


async def preguntar(ctx: Context, mensaje: str, formulario: type[BaseModel]):
    """QUE HACE : abre un dialogo y devuelve lo elegido, o None.

    COMO     : ctx.elicit() manda la pregunta al cliente y ESPERA.
               La tool se queda parada hasta que el humano responde.
    DEVUELVE : los datos si acepto. None en cualquier otro caso.
    POR QUE  : hay TRES desenlaces posibles y solo uno trae datos.
                 accept  -> el humano eligio        -> devolvemos data
                 decline -> dijo que no             -> None
                 cancel  -> cerro el dialogo        -> None
               Quien llama solo tiene que mirar si es None. Un solo if.
    FALLA SI : el cliente no sabe abrir dialogos (un cliente de prueba sin
               callback, por ejemplo). Lo capturamos: en vez de reventar,
               devolvemos None y la tool tira con los valores por defecto.
    """
    try:
        resultado = await ctx.elicit(message=mensaje, schema=formulario)
    except Exception as e:  # cliente sin capacidad de dialogo
        log(f"[profesor] sin dialogo disponible ({type(e).__name__}) -> por defecto")
        return None

    if resultado.action == "accept":
        return resultado.data

    log(f"[profesor] dialogo '{resultado.action}' -> por defecto")
    return None


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  ZONA 5 — LA TOOL                                                         ║
# ║  Que vive aqui : la funcion que CLAUDE decide llamar, sola.               ║
# ║  Tocas esto si : anades un parametro, o cambias cuando debe dispararse.   ║
# ╠═══════════════════════════════════════════════════════════════════════════╣
# ║     5a  DECORADOR   registra la funcion                                   ║
# ║     5b  FIRMA       los parametros -> se convierten en el schema          ║
# ║     5c  DOCSTRING   lo lee Claude para decidir SI usarla                  ║
# ║     5d  CUERPO      ELEGIR con .get(), RELLENAR con .format()             ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

# ── 5a. DECORADOR ─────────────────────────────────────────────────────────────
@mcp.tool(
    name="explicar",
    title="Explicar un tema",
)
# ── 5b. FIRMA ─────────────────────────────────────────────────────────────────
#      DOS CAMBIOS GORDOS RESPECTO A ANTES:
#
#      1) 'async def' en vez de 'def'. Hace falta porque dentro hay 'await':
#         la funcion se PARA a esperar la respuesta del humano y deja correr
#         otras cosas mientras. Una funcion normal no sabe pararse.
#
#      2) 'ctx: Context' es un parametro que CLAUDE NO VE.
#         Es la primera excepcion a la regla "la firma es el schema":
#         el SDK reconoce el tipo Context, lo rellena el solo, y lo saca
#         del JSON Schema. Compruebalo: el schema solo tendra 'tema'.
#
#      Y fijate en lo que YA NO esta: modo, nivel y tono han desaparecido.
#      Ahora se preguntan en el dialogo, asi que tenerlos aqui seria pedirlos
#      dos veces. La superficie de la tool se ha hecho MAS PEQUENA.
async def explicar(tema: str, ctx: Context) -> str:
    # ── 5c. DOCSTRING ─────────────────────────────────────────────────────────
    """Devuelve el andamiaje pedagógico para explicar un tema con prosa clara y directa.

    Úsala cuando la persona quiera ENTENDER algo, no solo resolverlo: preguntas
    del tipo "qué es X", "cómo funciona Y", "por qué Z", "explícame W".
    No la uses para tareas de ejecución pura (escribe este código, corrige este bug).

    Al ejecutarse abre un diálogo para que la persona elija el método de
    explicación y su extensión, y después los ajustes que ese método admita
    (nivel y tono en el clásico, solo nivel en el manual). No tienes que
    decidir tú esos valores: solo pasa el tema.

    El diálogo incluye la opción 'libre', que renuncia al andamiaje. Por eso
    puedes llamar a esta tool sin miedo a encorsetar la respuesta: si la
    persona no quiere método, lo dice ahí.

    Args:
        tema: El tema a explicar, tal como lo formuló la persona.

    Returns:
        Un bloque de instrucciones que debes seguir al pie de la letra para
        construir tu respuesta sobre el tema.
    """
    # ── 5d. CUERPO ────────────────────────────────────────────────────────────
    log(f"[profesor] explicar(tema={tema!r}) -> abriendo dialogo")

    # PASO 0 — arrancamos con los valores por defecto ya puestos.
    #   Asi, si el humano cancela en cualquier punto, ya hay respuesta valida.
    #   No hay ninguna rama del codigo que acabe sin datos.
    modo = POR_DEFECTO["modo"]
    nivel = POR_DEFECTO["nivel"]
    tono = POR_DEFECTO["tono"]
    extension = POR_DEFECTO["extension"]

    # PASO 1 — PREGUNTAR el metodo y la extension. Esto sale SIEMPRE.
    eleccion = await preguntar(
        ctx,
        f"¿Cómo quieres que te explique «{tema}»?",
        EleccionModo,
    )
    if eleccion is not None:
        modo = eleccion.modo
        extension = eleccion.extension

        # PASO 2 — LA CASCADA. Solo para los metodos que tienen algo que ajustar.
        #   Cornell, Feynman y libre no tienen huecos de nivel ni de tono,
        #   asi que preguntarlos no cambiaria nada. El dialogo no hace perder
        #   el tiempo con opciones sin efecto — y menos aun a quien acaba de
        #   pedir explicitamente que no le impongan forma.
        #
        #   Dos ramas y no una porque los dos metodos abiertos no lo son igual:
        #   'clasico' se modula en nivel y tono, 'manual' solo en nivel. Cada
        #   uno pregunta exactamente los ejes que su molde consume.
        if modo == "clasico":
            ajuste = await preguntar(
                ctx,
                "Ajusta la explicación clásica:",
                AjusteClasico,
            )
            if ajuste is not None:
                nivel = ajuste.nivel
                tono = ajuste.tono

        elif modo == "manual":
            ajuste = await preguntar(
                ctx,
                "¿Para quién se escribe el capítulo?",
                AjusteManual,
            )
            if ajuste is not None:
                nivel = ajuste.nivel

    log(
        f"[profesor] resuelto -> modo={modo!r}, nivel={nivel!r}, "
        f"tono={tono!r}, extension={extension!r}"
    )

    # PASO 3 — ELEGIR y RELLENAR.
    #   Da igual si los valores vienen de un dialogo, de un parametro o de
    #   un default: a partir de aqui son strings. Por eso anadir un eje solo
    #   ha costado una linea aqui y una linea en el .format().
    molde = MODOS.get(modo, MODOS["clasico"])
    ajuste_nivel = NIVELES.get(nivel, NIVELES["intermedio"])
    ajuste_tono = TONO.get(tono, TONO["formal"])
    ajuste_extension = EXTENSION.get(extension, EXTENSION["normal"])

    return molde.format(
        tema=tema,
        ajuste_nivel=ajuste_nivel,
        ajuste_tono=ajuste_tono,
        ajuste_extension=ajuste_extension,
        marcado=MARCADO,
    )


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  ZONA 6 — EL PROMPT                                                       ║
# ║  Que vive aqui : lo mismo que la tool, pero lo disparas TU con /profesor. ║
# ║  Tocas esto si : tocaste la ZONA 5. Van en pareja, siempre.               ║
# ╚═══════════════════════════════════════════════════════════════════════════╝


@mcp.prompt(
    name="profesor",
    title="Modo profesor",
    description="Fuerza una explicación estructurada y directa sobre un tema.",
)
def prompt_profesor(
    tema: str,
    modo: str = "clasico",
    nivel: str = "intermedio",
    tono: str = "formal",
    extension: str = "normal",
) -> str:
    """Plantilla que inyecta el andamiaje directamente en la conversación.

    Args:
        tema: Lo que quieres que te explique.
        modo: clasico | cornell | feynman | manual | libre (sin andamiaje).
        nivel: novato | intermedio | avanzado.  (afecta a 'clasico' y 'manual')
        tono: formal | out of the box.          (solo afecta a 'clasico')
        extension: normal | corto.              (afecta a todos los metodos)
    """
    log(
        f"[profesor] prompt(tema={tema!r}, modo={modo!r}, nivel={nivel!r}, "
        f"tono={tono!r}, extension={extension!r})"
    )
    # MISMO PATRON que la ZONA 5. Cuatro elecciones, un relleno.
    molde = MODOS.get(modo, MODOS["clasico"])
    ajuste_nivel = NIVELES.get(nivel, NIVELES["intermedio"])
    ajuste_tono = TONO.get(tono, TONO["formal"])
    ajuste_extension = EXTENSION.get(extension, EXTENSION["normal"])
    return molde.format(
        tema=tema,
        ajuste_nivel=ajuste_nivel,
        ajuste_tono=ajuste_tono,
        ajuste_extension=ajuste_extension,
        marcado=MARCADO,
    )


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  ZONA 7 — EL ARRANQUE                                                     ║
# ║  Que vive aqui : lo que convierte este archivo en un servidor.            ║
# ║  Tocas esto si : casi nunca. Cambia solo si pasas de stdio a HTTP.        ║
# ╚═══════════════════════════════════════════════════════════════════════════╝


def main() -> None:
    """Punto de entrada. Lo llama el script 'profesor-mcp' del pyproject.toml."""
    log("[profesor] arrancando en modo stdio")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
