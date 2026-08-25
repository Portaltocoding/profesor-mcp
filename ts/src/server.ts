#!/usr/bin/env node
// ╔═══════════════════════════════════════════════════════════════════════════╗
// ║  PROFESOR — servidor MCP en TypeScript                                    ║
// ║                                                                           ║
// ║  Gemelo de src/profesor_mcp/server.py. Misma tool, mismo prompt, mismas   ║
// ║  respuestas. Cambia el lenguaje y nada mas.                               ║
// ║                                                                           ║
// ║  Los TEXTOS no viven aqui: se generan desde el Python a ./moldes.ts.      ║
// ║  Aqui vive la MECANICA. Esa si esta escrita dos veces, porque cada SDK    ║
// ║  tiene la suya, y son las dos unicas cosas que hay que mantener a la par: ║
// ║  la cascada del dialogo y la forma de los formularios.                    ║
// ╠═══════════════════════════════════════════════════════════════════════════╣
// ║  ZONA 1  IMPORTS    traer herramientas de fuera                           ║
// ║  ZONA 2  SERVIDOR   identidad del servidor + log()                        ║
// ║  ZONA 3  MOLDES     importados del fichero generado                       ║
// ║  ZONA 4  DATOS      importados del fichero generado                       ║
// ║  ZONA 4.5 FORMULARIOS  la forma de las preguntas del dialogo              ║
// ║  ZONA 5  TOOL       la llama CLAUDE. Abre el dialogo.                     ║
// ║  ZONA 6  PROMPT     lo llamas TU. Verboso, sin dialogo.                   ║
// ║  ZONA 7  ARRANQUE   pone el servidor a escuchar                           ║
// ╚═══════════════════════════════════════════════════════════════════════════╝

// ╔═══════════════════════════════════════════════════════════════════════════╗
// ║  ZONA 1 — IMPORTS                                                         ║
// ╚═══════════════════════════════════════════════════════════════════════════╝

import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import type { ElicitRequestFormParams } from '@modelcontextprotocol/sdk/types.js';
import { z } from 'zod';

// ZONAS 3 y 4 — no se escriben, se generan. Fuente: server.py
import { MODOS, NIVELES, TONO, EXTENSION, MARCADO } from './moldes.js';

// ╔═══════════════════════════════════════════════════════════════════════════╗
// ║  ZONA 2 — EL SERVIDOR                                                     ║
// ║  Tocas esto si : cambias el nombre, la version, o como orientas a Claude. ║
// ╚═══════════════════════════════════════════════════════════════════════════╝

const mcp = new McpServer({
  name: 'profesor',
  title: 'Profesor',
  version: '0.1.0',
}, {
  instructions:
    "Servidor que impone una prosa explicativa, clara y directa. " +
    "Usa la tool 'explicar' cuando el usuario pida entender un tema, " +
    'no solo resolverlo.',
});

/**
 * QUE HACE : imprime para depurar.
 *
 * COMO     : escribe en stderr, que NO es el canal del protocolo.
 * FALLA SI : usas console.log() en su lugar. console.log() va a stdout,
 *            corrompe el JSON del protocolo, y el cliente desconecta el
 *            servidor sin explicacion. En Node la trampa es peor que en
 *            Python: console.log() es lo primero que escribe todo el mundo.
 */
function log(mensaje: string): void {
  console.error(mensaje);
}

/**
 * QUE HACE : rellena los {huecos} de un molde.
 *
 * POR QUE  : Python trae .format() de serie; JavaScript no trae nada
 *            equivalente, asi que el equivalente se escribe. Son seis lineas.
 * COMO     : sustituye {clave} por su valor para las claves que reciba.
 *            Un {hueco} sin valor se queda tal cual, igual de visible que un
 *            KeyError, pero sin tumbar la respuesta.
 * OJO      : replaceAll con string literal, no con expresion regular: los
 *            valores llevan parentesis, asteriscos y acentos, y una regex
 *            los interpretaria.
 */
function rellenar(molde: string, valores: Record<string, string>): string {
  let salida = molde;
  for (const [clave, valor] of Object.entries(valores)) {
    salida = salida.replaceAll(`{${clave}}`, valor);
  }
  return salida;
}

// ╔═══════════════════════════════════════════════════════════════════════════╗
// ║  ZONA 4.5 — LOS FORMULARIOS                                               ║
// ║  Que vive aqui : la FORMA de las preguntas que abre el dialogo.           ║
// ║  Tocas esto si : cambias que se pregunta o en que orden.                  ║
// ╠═══════════════════════════════════════════════════════════════════════════╣
// ║  DIFERENCIA CON PYTHON: alli son clases Pydantic y el SDK las traduce a   ║
// ║  JSON Schema por ti. Aqui la spec pide el JSON Schema directamente, asi   ║
// ║  que se escribe a mano. Es mas verboso y mas literal: lo que ves es       ║
// ║  exactamente lo que viaja por el cable.                                   ║
// ║                                                                           ║
// ║  LIMITE DE LA SPEC (identico en los dos lenguajes): solo tipos            ║
// ║  primitivos. Un 'enum' se pinta como selector, no como caja de texto.     ║
// ╚═══════════════════════════════════════════════════════════════════════════╝

/** PASO 1 del dialogo: siempre se pregunta esto.
 *
 *  Van juntos modo y extension porque los dos aplican SIEMPRE, elijas el
 *  metodo que elijas. Lo que solo vale para 'clasico' vive en el paso 2.
 *
 *  OJO: los valores DEBEN coincidir con las claves de MODOS y de EXTENSION.
 */
const ELECCION_MODO: ElicitRequestFormParams['requestedSchema'] = {
  type: 'object',
  properties: {
    modo: {
      type: 'string',
      title: 'Método',
      description: "Método de explicación ('libre' = sin andamiaje)",
      enum: ['clasico', 'cornell', 'feynman', 'manual', 'libre'],
      default: 'clasico',
    },
    extension: {
      type: 'string',
      title: 'Extensión',
      description: 'Extensión de la explicación',
      enum: ['normal', 'corto'],
      default: 'normal',
    },
  },
};

/** PASO 2 del dialogo: SOLO si en el paso 1 se eligio 'clasico'.
 *
 *  Cornell, Feynman y libre son metodos cerrados: preguntarles nivel o tono
 *  no tendria efecto, asi que ni se pregunta.
 */
const AJUSTE_CLASICO: ElicitRequestFormParams['requestedSchema'] = {
  type: 'object',
  properties: {
    nivel: {
      type: 'string',
      title: 'Nivel',
      description: 'Profundidad asumida',
      enum: ['novato', 'intermedio', 'avanzado'],
      default: 'intermedio',
    },
    tono: {
      type: 'string',
      title: 'Tono',
      description: 'Registro de la prosa',
      enum: ['formal', 'out of the box'],
      default: 'formal',
    },
  },
};

/** PASO 2 alternativo: SOLO si en el paso 1 se eligio 'manual'.
 *
 *  Un formulario propio, y no el de 'clasico', por una sola razon: el manual
 *  no tiene hueco de tono. Si reutilizaramos AJUSTE_CLASICO, el desplegable
 *  preguntaria un tono que rellenar() tira a la basura sin decir nada.
 *  Preguntar algo que no cambia la respuesta es peor que no preguntarlo:
 *  promete un control que no existe.
 */
const AJUSTE_MANUAL: ElicitRequestFormParams['requestedSchema'] = {
  type: 'object',
  properties: {
    nivel: {
      type: 'string',
      title: 'Nivel',
      description: 'Para quién se escribe el capítulo (fija el contrato de entrada)',
      enum: ['novato', 'intermedio', 'avanzado'],
      default: 'intermedio',
    },
  },
};

// QUE HACE : los valores con los que se responde si el humano cancela.
// POR QUE  : cancelar no puede dejar la tool sin datos. Un solo sitio
//            donde estan definidos, para no repetirlos por el codigo.
const POR_DEFECTO = {
  modo: 'clasico',
  nivel: 'intermedio',
  tono: 'formal',
  extension: 'normal',
} as const;

/**
 * QUE HACE : abre un dialogo y devuelve lo elegido, o null.
 *
 * COMO     : elicitInput() manda la pregunta al cliente y ESPERA. La tool se
 *            queda parada hasta que el humano responde.
 * DEVUELVE : los datos si acepto. null en cualquier otro caso.
 * POR QUE  : hay TRES desenlaces posibles y solo uno trae datos.
 *              accept  -> el humano eligio        -> devolvemos content
 *              decline -> dijo que no             -> null
 *              cancel  -> cerro el dialogo        -> null
 *            Quien llama solo tiene que mirar si es null. Un solo if.
 * FALLA SI : el cliente no sabe abrir dialogos. Lo capturamos: en vez de
 *            reventar, devolvemos null y la tool tira con los defaults.
 */
async function preguntar(
  mensaje: string,
  formulario: ElicitRequestFormParams['requestedSchema'],
): Promise<Record<string, unknown> | null> {
  let resultado;
  try {
    resultado = await mcp.server.elicitInput({
      message: mensaje,
      requestedSchema: formulario,
    });
  } catch (e) {
    const nombre = e instanceof Error ? e.constructor.name : typeof e;
    log(`[profesor] sin dialogo disponible (${nombre}) -> por defecto`);
    return null;
  }

  if (resultado.action === 'accept' && resultado.content) {
    return resultado.content;
  }

  log(`[profesor] dialogo '${resultado.action}' -> por defecto`);
  return null;
}

/** QUE HACE : lee un campo del formulario solo si es un string.
 *
 *  POR QUE  : content llega tipado como unknown — el cliente podria mandar
 *             cualquier cosa. Si no es un string, nos quedamos con el valor
 *             que ya teniamos en vez de meter basura en el molde.
 */
function texto(datos: Record<string, unknown>, campo: string, previo: string): string {
  const valor = datos[campo];
  return typeof valor === 'string' ? valor : previo;
}

// ╔═══════════════════════════════════════════════════════════════════════════╗
// ║  ZONA 5 — LA TOOL                                                         ║
// ║  Que vive aqui : la funcion que CLAUDE decide llamar, sola.               ║
// ║  Tocas esto si : anades un parametro, o cambias cuando debe dispararse.   ║
// ╚═══════════════════════════════════════════════════════════════════════════╝

mcp.registerTool(
  'explicar',
  {
    title: 'Explicar un tema',
    // La DESCRIPCION la lee Claude para decidir SI usarla. En Python esto es
    // el docstring; aqui es un campo. Mismo texto, mismo papel.
    description: [
      'Devuelve el andamiaje pedagógico para explicar un tema con prosa clara y directa.',
      '',
      'Úsala cuando la persona quiera ENTENDER algo, no solo resolverlo: preguntas',
      'del tipo "qué es X", "cómo funciona Y", "por qué Z", "explícame W".',
      'No la uses para tareas de ejecución pura (escribe este código, corrige este bug).',
      '',
      'Al ejecutarse abre un diálogo para que la persona elija el método de',
      'explicación y su extensión, y después los ajustes que ese método admita',
      '(nivel y tono en el clásico, solo nivel en el manual). No tienes que',
      'decidir tú esos valores: solo pasa el tema.',
      '',
      "El diálogo incluye la opción 'libre', que renuncia al andamiaje. Por eso",
      'puedes llamar a esta tool sin miedo a encorsetar la respuesta: si la',
      'persona no quiere método, lo dice ahí.',
    ].join('\n'),
    // La FIRMA se convierte en el schema. Solo 'tema': modo, nivel y tono se
    // preguntan en el dialogo, y tenerlos aqui seria pedirlos dos veces.
    inputSchema: {
      tema: z.string().describe('El tema a explicar, tal como lo formuló la persona.'),
    },
  },
  async ({ tema }) => {
    log(`[profesor] explicar(tema=${JSON.stringify(tema)}) -> abriendo dialogo`);

    // PASO 0 — arrancamos con los valores por defecto ya puestos.
    //   Asi, si el humano cancela en cualquier punto, ya hay respuesta valida.
    //   No hay ninguna rama del codigo que acabe sin datos.
    let modo: string = POR_DEFECTO.modo;
    let nivel: string = POR_DEFECTO.nivel;
    let tono: string = POR_DEFECTO.tono;
    let extension: string = POR_DEFECTO.extension;

    // PASO 1 — PREGUNTAR el metodo y la extension. Esto sale SIEMPRE.
    const eleccion = await preguntar(
      `¿Cómo quieres que te explique «${tema}»?`,
      ELECCION_MODO,
    );

    if (eleccion !== null) {
      modo = texto(eleccion, 'modo', modo);
      extension = texto(eleccion, 'extension', extension);

      // PASO 2 — LA CASCADA. Solo para los metodos que tienen algo que ajustar.
      //   Dos ramas y no una porque los dos metodos abiertos no lo son igual:
      //   'clasico' se modula en nivel y tono, 'manual' solo en nivel. Cada
      //   uno pregunta exactamente los ejes que su molde consume.
      if (modo === 'clasico') {
        const ajuste = await preguntar('Ajusta la explicación clásica:', AJUSTE_CLASICO);
        if (ajuste !== null) {
          nivel = texto(ajuste, 'nivel', nivel);
          tono = texto(ajuste, 'tono', tono);
        }
      } else if (modo === 'manual') {
        const ajuste = await preguntar('¿Para quién se escribe el capítulo?', AJUSTE_MANUAL);
        if (ajuste !== null) {
          nivel = texto(ajuste, 'nivel', nivel);
        }
      }
    }

    log(
      `[profesor] resuelto -> modo=${JSON.stringify(modo)}, nivel=${JSON.stringify(nivel)}, ` +
      `tono=${JSON.stringify(tono)}, extension=${JSON.stringify(extension)}`,
    );

    // PASO 3 — ELEGIR y RELLENAR.
    return { content: [{ type: 'text' as const, text: construir(tema, modo, nivel, tono, extension) }] };
  },
);

/** QUE HACE : elige el molde y lo rellena.
 *
 *  POR QUE ESTA APARTE: la ZONA 5 y la ZONA 6 hacen exactamente esto mismo, y
 *  en Python el bloque esta escrito dos veces. Aqui se escribe una. Si algun
 *  dia divergen, que sea porque alguien lo decidio, no porque se le olvido
 *  tocar el segundo sitio.
 *
 *  OJO: los ?? replican el .get(clave, default) de Python. Una clave que no
 *  existe cae al valor por defecto en vez de meter 'undefined' en el molde.
 */
function construir(
  tema: string,
  modo: string,
  nivel: string,
  tono: string,
  extension: string,
): string {
  return rellenar(MODOS[modo] ?? MODOS['clasico']!, {
    tema,
    ajuste_nivel: NIVELES[nivel] ?? NIVELES['intermedio']!,
    ajuste_tono: TONO[tono] ?? TONO['formal']!,
    ajuste_extension: EXTENSION[extension] ?? EXTENSION['normal']!,
    marcado: MARCADO,
  });
}

// ╔═══════════════════════════════════════════════════════════════════════════╗
// ║  ZONA 6 — EL PROMPT                                                       ║
// ║  Que vive aqui : lo mismo que la tool, pero lo disparas TU con /profesor. ║
// ║  Tocas esto si : tocaste la ZONA 5. Van en pareja, siempre.               ║
// ╚═══════════════════════════════════════════════════════════════════════════╝

mcp.registerPrompt(
  'profesor',
  {
    title: 'Modo profesor',
    description: 'Fuerza una explicación estructurada y directa sobre un tema.',
    argsSchema: {
      tema: z.string().describe('Lo que quieres que te explique.'),
      modo: z.string().optional().describe('clasico | cornell | feynman | manual | libre (sin andamiaje).'),
      nivel: z.string().optional().describe("novato | intermedio | avanzado. (afecta a 'clasico' y 'manual')"),
      tono: z.string().optional().describe("formal | out of the box. (solo afecta a 'clasico')"),
      extension: z.string().optional().describe('normal | corto. (afecta a todos los metodos)'),
    },
  },
  ({ tema, modo, nivel, tono, extension }) => {
    const m = modo ?? POR_DEFECTO.modo;
    const n = nivel ?? POR_DEFECTO.nivel;
    const t = tono ?? POR_DEFECTO.tono;
    const e = extension ?? POR_DEFECTO.extension;
    log(
      `[profesor] prompt(tema=${JSON.stringify(tema)}, modo=${JSON.stringify(m)}, ` +
      `nivel=${JSON.stringify(n)}, tono=${JSON.stringify(t)}, extension=${JSON.stringify(e)})`,
    );
    return {
      messages: [{
        role: 'user' as const,
        content: { type: 'text' as const, text: construir(tema, m, n, t, e) },
      }],
    };
  },
);

// ╔═══════════════════════════════════════════════════════════════════════════╗
// ║  ZONA 7 — EL ARRANQUE                                                     ║
// ║  Que vive aqui : lo que convierte este archivo en un servidor.            ║
// ║  Tocas esto si : casi nunca. Cambia solo si pasas de stdio a HTTP.        ║
// ╚═══════════════════════════════════════════════════════════════════════════╝

async function main(): Promise<void> {
  log('[profesor] arrancando en modo stdio');
  await mcp.connect(new StdioServerTransport());
}

main().catch((e) => {
  log(`[profesor] fallo al arrancar: ${e}`);
  process.exit(1);
});
