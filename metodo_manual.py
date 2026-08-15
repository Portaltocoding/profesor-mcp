"""MOLDE_MANUAL: el metodo 'manual'.

QUE ES     : un quinto molde para la ZONA 3 de src/profesor_mcp/server.py.
DE DONDE   : destilado de 18 hilos de Reddit (r/math, r/PhysicsStudents,
             r/computerscience, r/MachineLearning, r/askphilosophy,
             r/AskHistorians, r/chemistry, r/biology y otros) donde se discute
             que hace que un libro de texto explique BIEN, no que sea famoso.
             Corpus y datos: ~/Downloads/libros-explicativos/
QUE HACE   : produce una explicacion con la arquitectura de un capitulo de
             manual bien escrito. Es el molde LARGO: donde 'clasico' da seis
             apartados, este da doce y no permite saltarse ninguno.

╔═══════════════════════════════════════════════════════════════════════════╗
║  LAS SIETE LEYES QUE SALEN DEL CORPUS                                     ║
╠═══════════════════════════════════════════════════════════════════════════╣
║  1. PENDIENTE LINEAL                                                      ║
║     "lucid with just the right amount of handholding and a pretty linear   ║
║      increase in difficulty, so you always feel challenged, without        ║
║      feeling overwhelmed"  (Hammack, Book of Proof, +71)                   ║
║     El salto de dificultad es el fallo numero uno. No hay escalones.       ║
║                                                                           ║
║  2. INTUICION SIN PERDER RIGOR (nunca una en lugar de la otra)             ║
║     "he really does a good job in building the intuition without losing    ║
║      much rigour"  (r/computerscience)                                     ║
║     "gives intuition while also providing you with details" (Bredon)       ║
║     "rigorous, yet concepts are well motivated" (Apostol, Bartle)          ║
║                                                                           ║
║  3. PROHIBIDO EL HANDWAVING                                                ║
║     "students find their first introduction to differential topology to    ║
║      be extremely handwavy... Tu does a great job of explaining            ║
║      everything systematically and rigorously"  (Tu, +198)                 ║
║     "proofs are always given in full detail"  (Katok-Hasselblatt)          ║
║     Cae aqui todo "se puede demostrar que", "es facil ver que", "obvio".   ║
║                                                                           ║
║  4. MOTIVAR ANTES DE DEFINIR                                               ║
║     "the only one that cares about motivating these things beyond getting  ║
║      nice functorial diagrams"  (Cox, Primes of the Form x2+ny2, +30)      ║
║     "I would have benefitted a lot from the intuition about varieties"     ║
║      (lamento de quien se salto el capitulo de motivacion)                 ║
║                                                                           ║
║  5. DECLARAR PRERREQUISITOS Y RENUNCIAS                                    ║
║     "completely accessible to anyone who knows calculus and nothing else"  ║
║      (Arnold, Abel's Theorem)                                              ║
║     "it eschews mathematical rigour for clarity"  (Strogatz, y AUN ASI     ║
║      es de los mejor escritos: porque la renuncia esta declarada)          ║
║                                                                           ║
║  6. CONVERSACIONAL Y PRECISO A LA VEZ                                      ║
║     "written in an almost conversational manner, yet very precise (you     ║
║      have to read every word carefully)"  (Herstein, Topics in Algebra)    ║
║                                                                           ║
║  7. NINGUN CONCEPTO SE USA ANTES DE EXISTIR                                ║
║     "What's hard in philosophy is context. If you don't understand the      ║
║      references, the whole thing is moot"  (r/philosophy)                   ║
║     "completely accessible to anyone who knows calculus and nothing else"   ║
║      (Arnold: el contrato lexico resuelto en una linea)                     ║
║     "I would have benefitted a lot from the intuition about varieties"      ║
║      (el que se salto el capitulo previo: la dependencia se cobra sola)     ║
║     El orden de un capitulo NO es el orden logico del experto: es el orden  ║
║     de dependencias del que aun no sabe. Se ordena para que ningun termino  ║
║     haga falta antes de estar definido, y lo que no cabe en ese orden se    ║
║     dice en lenguaje llano hasta que le llegue su turno.                    ║
║                                                                            ║
║  8. EJERCICIOS QUE ENSENAN, NO QUE MIDEN                                    ║
║     "great exercises (with solutions)... some insight how proofs are       ║
║      really found"  (Concrete Mathematics)                                 ║
║     "every chapter ends with genuinely hard problems"  (Morin)             ║
║     Y el reproche a las Feynman Lectures, el libro mas alabado del corpus: ║
║     su unico defecto citado es la falta de problemas.                      ║
╚═══════════════════════════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════════════════════════╗
║  LA TENSION QUE ESTE MOLDE RESUELVE                                       ║
╠═══════════════════════════════════════════════════════════════════════════╣
║  Del propio corpus, +5 votos, y es la pregunta mas lucida del hilo:       ║
║    "I wonder what standards people have for a well-written textbook.      ║
║     Concise and clear to an expert? Or intuitive and readable for a       ║
║     beginner? I know of no textbook which I would regard as well-written  ║
║     at all by the second standard."                                       ║
║                                                                           ║
║  No son el mismo libro. Por eso este molde es ABIERTO: consume            ║
║  {ajuste_nivel}. El nivel no decora la explicacion, decide QUE ES el      ║
║  contrato de entrada, y por tanto que puede darse por sabido sin mentir.  ║
║  Un manual sin audiencia declarada es el que "explica mal a todos".       ║
╚═══════════════════════════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════════════════════════╗
║  VERIFICACION CONTRA FUENTES PRIMARIAS                                    ║
╠═══════════════════════════════════════════════════════════════════════════╣
║  Las leyes de arriba salen de lo que dicen los LECTORES. Para saber cuales ║
║  son ademas doctrina declarada por los AUTORES, se leyeron los prefacios   ║
║  de cinco textos de matematicas de acceso libre (PDFs en                   ║
║  ~/Downloads/libros-explicativos/prefacios/):                              ║
║    Hammack, Book of Proof · Wilf, generatingfunctionology · Hatcher,       ║
║    Algebraic Topology · Riehl, Category Theory in Context · Vakil,         ║
║    The Rising Sea                                                          ║
║                                                                            ║
║  DECLARADO POR LOS AUTORES (ley confirmada, no inferida):                 ║
║   · Motivar y exigir el porque:                                            ║
║     "When introduced to a new idea, always ask why you should care. Do not  ║
║      expect an answer right away, but demand an answer eventually."        ║
║     "Hold tight to your geometric motivation."           (Vakil, 0.1)      ║
║   · Un ejemplo concreto por cada abstraccion:                              ║
║     "Try at least to apply any new abstraction to some concrete example    ║
║      you can understand well."                           (Vakil, 0.1)      ║
║   · Prerrequisitos nombrados uno a uno, con donde estudiarlos:             ║
║     "the present book assumes... In particular, the reader should know     ║
║      about quotient spaces... Good sources for this concept are [...]"     ║
║                                                          (Hatcher)        ║
║   · Renuncias declaradas: la ley mas confirmada, aparece en los CINCO.     ║
║     "Not included in this book is... spectral sequences" (Hatcher)         ║
║     "The subject is so vast that I have not attempted to give a            ║
║      comprehensive discussion."                          (Wilf)           ║
║   · Miniaturas antes del caso general: los titulos de Wilf lo hacen        ║
║     literalmente ("A slightly harder two term recurrence" tras resolver    ║
║     entera la version facil).                                              ║
║   · Elegir bien el primitivo:                                              ║
║     "Practitioners often assert that the hard part of category theory is   ║
║      to state the correct definitions."                  (Riehl)          ║
║                                                                            ║
║  NO DECLARADO EN NINGUN PREFACIO (sigue siendo inferencia, uselo asi):     ║
║   · el contraejemplo que justifica cada hipotesis                          ║
║   · ensenar como se le ocurre a uno el argumento                           ║
║   Se practican dentro de los textos, pero ningun autor los enuncia como    ║
║   metodo. Trato honesto: son observacion nuestra, no doctrina suya.        ║
║                                                                            ║
║  LO QUE LA EVIDENCIA CORRIGIO (dos leyes nuevas, 9 y 10):                  ║
║   9. DESCRIBIR LA FORMA DE LA DIFICULTAD, no solo avisar de que la hay.    ║
║      "Understanding algebraic geometry is often thought to be hard         ║
║       because it consists of large complicated pieces of machinery. In     ║
║       fact the opposite is true; rather than being narrow and deep, it is  ║
║       shallow but extremely broad."                      (Vakil, 0.1)     ║
║      Sirve para que el lector no atribuya mal su propio atasco.            ║
║  10. RUTAS DE LECTURA: que se puede saltar y a que coste. En los CINCO.    ║
║      "Chapter 10, on induction, can also be omitted with no break in       ║
║       continuity."                                       (Hammack)        ║
║      "this whole chapter could be skipped now, to be referred back to      ║
║       later for basic definitions."                      (Hatcher)        ║
║      "may be omitted at a first reading."                (Wilf)           ║
║      Vakil marca con ⋆ y ⋆⋆ el material avanzado.                          ║
║                                                                            ║
║  UNA TENSION REAL ENTRE AUTORES, sin resolver a proposito:                 ║
║    Vakil: "[los ejercicios] are not just an excuse to push hard material   ║
║           out of the text", y los intercala en la exposicion.              ║
║    Riehl: "the proofs of several propositions are left as exercises, with  ║
║           confidence that the reader will eventually find it more          ║
║           efficient to supply their own arguments than to read the         ║
║           author's."                                                       ║
║    No dicen lo mismo. La sintesis que adopta este molde es la de Vakil     ║
║    con la excepcion de Riehl declarada: se puede dejar una demostracion    ║
║    al lector si se dice que se hace y por que, nunca para esconder lo      ║
║    dificil.                                                                ║
╚═══════════════════════════════════════════════════════════════════════════╝

INSTALACION (RECETA A del server.py, cuatro toques):
  1) ZONA 3  ->  pega MOLDE_MANUAL (o importalo de aqui)
  2) ZONA 3  ->  MODOS["manual"] = MOLDE_MANUAL
  3) ZONA 5  ->  Literal[..., "manual"] en EleccionModo.modo
  4) ZONA 5  ->  la cascada: if modo in ("clasico", "manual"):
                 y en AjusteClasico preguntar solo 'nivel' cuando sea manual,
                 o dejar que el tono se ignore, que format lo descarta solo.
  (ZONA 6, el prompt, no necesita nada: ya hace MODOS.get(modo).)
"""

# ── MOLDE 5: MANUAL (abierto: consume nivel; ignora tono) ─────────────────────
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
