// ╔══════════════════════════════════════════════════════════════════╗
// ║  FICHERO GENERADO — no lo edites a mano.                         ║
// ║                                                                  ║
// ║  Fuente de verdad : src/profesor_mcp/server.py (ZONAS 3 y 4)     ║
// ║  Regenerar        : uv run python generar_ts.py                  ║
// ║                                                                  ║
// ║  Si cambias un molde aqui, la proxima regeneracion te lo pisa    ║
// ║  y las dos versiones del servidor volveran a explicar igual.     ║
// ╚══════════════════════════════════════════════════════════════════╝

export const MOLDE_CLASICO = `Explica **{tema}** siguiendo exactamente esta estructura, sin saltarte pasos:

1. **Qué es** — Una sola frase, directa, exponiendo el concepto y las partes que
   lo conforman. Sin rodeos, sin "es un concepto que...".
2. **El modelo mental** — Una analogía concreta con algo que ya se conoce.
   Di explícitamente en qué punto la analogía deja de funcionar.
3. **El mecanismo** — Cómo funciona por dentro, paso a paso, en orden causal
   y secuencial. Cada paso debe responder "y entonces qué pasa".
4. **Ejemplo mínimo** — El caso más pequeño posible que aún sea real.
   Nada de \`foo\`/\`bar\` si el tema admite un ejemplo del mundo real.
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
`;

export const MOLDE_CORNELL = `Explica **{tema}** con el método Cornell. Divide la respuesta en tres bloques,
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
`;

export const MOLDE_FEYNMAN = `Explica **{tema}** con el método Feynman. Cuatro pasos, en este orden y con
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
`;

export const MOLDE_MANUAL = `Explica **{tema}** como lo haria un capitulo de un libro de texto de los que se
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
- **Formato**: un bloque \`\`\`mermaid cuando la figura sea de cajas, flechas,
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
`;

export const MOLDE_LIBRE = `Explica **{tema}** sin andamiaje.

No apliques ningún método fijo. Sin apartados obligatorios, sin analogía de
oficio, sin pregunta de comprobación al final. Elige tú la forma que mejor le
venga al tema y responde como responderías si nadie te hubiera dado un guion.

{ajuste_extension}

{marcado}
`;

export const MODOS: Record<string, string> = {
  "clasico": MOLDE_CLASICO,
  "cornell": MOLDE_CORNELL,
  "feynman": MOLDE_FEYNMAN,
  "manual": MOLDE_MANUAL,
  "libre": MOLDE_LIBRE,
};

export const NIVELES: Record<string, string> = {
  "novato": `Nivel NOVATO: asume cero conocimiento previo del área. Define cada término técnico la primera vez que aparezca. Prioriza la analogía y el ejemplo por encima del mecanismo interno.`,
  "intermedio": `Nivel INTERMEDIO: asume que se conocen los fundamentos del área pero no este tema concreto. Ve directo al mecanismo. Compara con conceptos vecinos que ya se dominan.`,
  "avanzado": `Nivel AVANZADO: asume dominio del área. Salta la analogía si no aporta. Céntrate en los casos límite, las decisiones de diseño y el porqué de que esté hecho así y no de otra forma.`,
};

export const TONO: Record<string, string> = {
  "formal": `Tono FORMAL: explicación clásica y de libro sobre la materia. Sin abusar de oraciones subordinadas ni de conectores innecesarios. Va al grano: directo y seco. Prosa seria y poco relacional.`,
  "out of the box": `Tono OUT OF THE BOX: pensamiento lateral sobre el concepto, ajustado al nivel indicado. Busca las conexiones que no se ven a priori y los ángulos muertos del tema. Señala qué asunciones da por buenas todo el mundo sin comprobarlas.`,
};

export const EXTENSION: Record<string, string> = {
  "normal": `Extensión NORMAL: desarrolla cada apartado o punto hasta que quede entendido. Ni alargues por alargar ni recortes el mecanismo o los fallos, que son lo que de verdad enseña.`,
  "corto": `Extensión CORTA: no dejes fuera ningún apartado ni ningún punto que fueras a cubrir, pero reduce cada uno a su núcleo: tres frases como máximo. Un solo ejemplo. Una sola analogía. Nada de listas anidadas. Si algo no cabe en tres frases, sobra texto: no falta espacio.`,
};

export const MARCADO = `Marcado del texto:
- Cada término técnico va entre \`backticks\` la primera vez que aparece, y solo
  la primera. Si lo repites en cada línea deja de destacar nada.
- Si titulas secciones, ponlas en **negrita**.
- No escribas el color a mano: nada de códigos ANSI ni de HTML. Tú marcas,
  el cliente pinta. Lo que en tu terminal sería color, en otro cliente sería
  basura en mitad de la frase.
`;
