import sqlite3
import os
from flask import current_app
from contextlib import closing
from werkzeug.security import generate_password_hash

# DB_PATH = os.path.join(current_app.root_path, "instance", "database.db")


def get_db_connection():
    db_path = os.path.join(current_app.root_path, "instance", "database.db")
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with closing(get_db_connection()) as conn:
        cursor = conn.cursor()

        # Crear tabla usuarios
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            );
            """
        )

        # Crear tabla asignaturas con nombre único
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS asignaturas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE,
                descripcion TEXT
            );
            """
        )

        # Crear tabla temas con unicidad en asignatura_id y titulo
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS temas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asignatura_id INTEGER,
                usuario_id INTEGER,
                titulo TEXT NOT NULL,
                contenido TEXT NOT NULL,
                es_fijo INTEGER NOT NULL DEFAULT 0,
                UNIQUE(asignatura_id, titulo),
                FOREIGN KEY (asignatura_id) REFERENCES asignaturas(id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            );
            """
        )

        # Crear tabla examenes con unicidad en asignatura_id y nombre
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS examenes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asignatura_id INTEGER,
                nombre TEXT NOT NULL,
                UNIQUE(asignatura_id, nombre),
                FOREIGN KEY (asignatura_id) REFERENCES asignaturas(id)
            );
            """
        )

        # Crear tabla preguntas con unicidad en examen_id y texto
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS preguntas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                examen_id INTEGER,
                texto TEXT NOT NULL,
                UNIQUE(examen_id, texto),
                FOREIGN KEY (examen_id) REFERENCES examenes(id)
            );
            """
        )

        # Crear tabla opciones con unicidad en pregunta_id y texto
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS opciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pregunta_id INTEGER,
                texto TEXT NOT NULL,
                es_correcta INTEGER NOT NULL DEFAULT 0,
                UNIQUE(pregunta_id, texto),
                FOREIGN KEY (pregunta_id) REFERENCES preguntas(id)
            );
            """
        )

        # Crear tabla intentos_examen
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS intentos_examen (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER,
                examen_id INTEGER,
                porcentaje_acierto REAL,
                respuestas_correctas INTEGER DEFAULT 0,
                respuestas_incorrectas INTEGER DEFAULT 0,
                fecha TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
                FOREIGN KEY (examen_id) REFERENCES examenes(id)
            );
            """
        )

        # Limpiar duplicados existentes antes de insertar
        cursor.execute(
            """
            DELETE FROM temas
            WHERE id NOT IN (
                SELECT MIN(id)
                FROM temas
                GROUP BY asignatura_id, titulo
            )
            """
        )
        cursor.execute(
            """
            DELETE FROM examenes
            WHERE id NOT IN (
                SELECT MIN(id)
                FROM examenes
                GROUP BY asignatura_id, nombre
            )
            """
        )
        cursor.execute(
            """
            DELETE FROM preguntas
            WHERE id NOT IN (
                SELECT MIN(id)
                FROM preguntas
                GROUP BY examen_id, texto
            )
            """
        )
        cursor.execute(
            """
            DELETE FROM opciones
            WHERE id NOT IN (
                SELECT MIN(id)
                FROM opciones
                GROUP BY pregunta_id, texto
            )
            """
        )
        conn.commit()

        # Insertar usuarios iniciales
        usuarios = [
            ("usuario1", generate_password_hash("password1")),
            ("usuario2", generate_password_hash("password2")),
        ]
        cursor.executemany(
            "INSERT OR IGNORE INTO usuarios (username, password) VALUES (?, ?)",
            usuarios,
        )

        # Insertar asignaturas
        asignaturas = [
            ("El comentario de texto", "Teoría y práctica"),
            ("Lengua Española", "Manual de lengua Española"),
            ("Inglés", "Curso de Inglés para adultos"),
            ("Informática", "Introducción a la informática básica"),
            ("Matemáticas", "Volumen 1 y volumen 2"),
        ]
        cursor.executemany(
            "INSERT OR IGNORE INTO asignaturas (nombre, descripcion) VALUES (?, ?)",
            asignaturas,
        )

        # Insertar temas
        temas = [
            (
                1,
                None,
                "Capítulo 1: ¿Qué es un texto?",
                """
## **I. Definición de Texto**

1. **Concepto**: Un texto es un acto de comunicación que transmite un mensaje coherente y autónomo entre un emisor y un receptor, con una intención comunicativa clara.
    - **Características principales**:
        - Puede ser **oral** (una conversación, un discurso) o **escrito** (un libro, un correo).
        - No depende de su **extensión**, sino de su capacidad para transmitir un mensaje interpretable. Un texto breve como "¡Socorro!" puede ser tan válido como una novela extensa.
        - Debe ser **coherente** (tener sentido lógico) y **autónomo** (no depender de otro texto para ser comprendido).
    - **Importancia de la intención comunicativa**: Todo texto tiene un propósito, como informar, persuadir, entretener o expresar emociones. Por ejemplo, un cartel que dice "Prohibido fumar" busca regular una conducta, mientras que un poema busca evocar sentimientos.

2. **Ejemplos prácticos**:
    - **Simples**:
        - "¡Socorro!" (un grito pidiendo ayuda, claro y directo).
        - "Cierren la puerta" (una instrucción breve en un contexto específico).
    - **Complejos**:
        - Una novela como *Cien años de soledad* de Gabriel García Márquez, que narra generaciones de una familia con múltiples tramas.
        - Un ensayo filosófico como *El mundo de Sofía* de Jostein Gaarder, que explica conceptos abstractos
        a través de una historia.
        - Una noticia periodística que informa sobre un evento reciente, como "Terremoto de magnitud 6 sacude la costa
        de Japón".
    - **Ejemplo intermedio:** Un correo electrónico formal invitando a una reunión: "Estimados colegas, les
    invitamos a la reunión del próximo lunes a las 10:00 para discutir el proyecto X. Saludos cordiales".

## **II. Constituyentes del Texto**

1. **Emisor o Productor:**
    - **Definición:** Es quien produce el texto, ya sea un individuo (una persona que escribe una carta) o un 
    colectivo (una organización como la Asamblea Constituyente que redacta una constitución).
    - **Influencia del contexto:**
        - **Tiempo:** El momento en que se emite el mensaje afecta su interpretación. Por ejemplo, "Nos veremos
        mañana" depende del día en que se dice (si se dice un lunes, "mañana" es martes).
        - **Espacio:** El lugar desde donde se emite también influye. Un cartel que dice "Prohibido estacionar
        aquí" tiene sentido solo en el lugar donde está ubicado.
    - **Ejemplo práctico:**
        - Un discurso político emitido en 2020 durante la pandemia (como "Debemos quedarnos en casa") refleja
        un contexto histórico específico que no sería igual en 2025.
        - Una carta escrita por un estudiante desde España a un amigo en México incluirá referencias culturales
        o geográficas específicas ("Hace frío en Madrid").

2. **Receptor o Destinatario:**
    - **Definición:** Es a quien va dirigido el mensaje, pudiendo ser específico (una persona concreta) o genérico
    (un público amplio).
    - **Tipos de receptores:**
        - **Específico: Una carta dirigida a "Raúl" o un mensaje de texto a un amigo ("¿Nos vemos a las 6, Ana?").
        - **Genérico:** Un libro dirigido a todos los lectores interesados (como *Harry Potter*), o un cartel público
        ("No tirar basura").
    - **Influencia en la interpretación:**
        - Un receptor específico interpreta el mensaje según su relación con el emisor. Por ejemplo, en "Raul", te espero
        en casa", Raúl sabe exactamente de qué casa se trata.
        - Un receptor genérico debe inferir más. En un cartel que dice "Cuiden el parque", cada persona lo interpreta
        según su contexto (un niño podría pensar en no ensuciar, un adulto en no dañar las plantas).
    - **Ejemplo práctico:**
        - Un anuncio de televisón que dice "¡Compra ahora!" está dirigido a un público genérico (consumidores),
        pero cada persona lo interpretará según sus necesidades (alguien que necesita un teléfono no verá de forma
        diferente a alguien que no).

3. **Mensaje:**
    - **Definición:** Es el contenido que se transmite, que puede ser simple o complejo, explícito o implícito.
    - **Tipos de contenido:**
        - **Explícito:** Información directa, como "Cierren la puerta" (una instrucción clara).
        - **Implícito:** Información que se deduce del contexto, como "Hace frío" (puede implicar "Abrígate" o
        "Cierra la ventana").
    - **Variedad de mensajes:**
        - **Simples:** "No corras" (una orden directa).
        - **Complejos:** Un artículo periodístico que analiza las causas de la inflación, con datos, argumentos
        y conclusiones.
    - **Ejemplo práctico:**
        - En un cuento infantil como *Caperucita Roja*, el mensaje explícito es la historia de una niña que visita
        a su abuela, pero el mensaje implícito puede ser "No hagas caso a desconocidos".
        - En un discurso político: "Es hora de un cambio" puede implicar críticas al gobierno actual y una
        propuesta de nuevas políticas.

## **III. Organización del Texto**

1. **Microestructura:**
    - **Definición:** Es el nivel más detallado del texto, que incluye el contenido explícito (lo que se dice
    directamente) y el implícito (lo que se deduce del contexto).
    - **Características:**
        - Contiene las ideas específicas y los detalles del texto.
        - Incluye información implícita que depende del contexto cultural, social o situacional.
    - **Ejemplo práctico:**
        - Texto: "Pedro envió una carta a María".
            - **Explícito:** Pedro mandó una carta.
            - **Implícito:** Probablemente usó el correo (en un contexto tradicional) o un correo electrónico (en 
            un contexto moderno); María es alguien conocido para Pedro.
        - En un diálogo: "Hace calor, ¿no?" puede implicar "Abre la ventana" o "Enciende el ventilador",
        dependiendo del contexto.

2. **Macroestructura:**
    - **Definición:** Es un resumen que condensa las ideas esenciales del texto, eliminando detalles secundarios
    y transformando la información en ideas generales.
    - **Proceso para construirla:**
        1. **Eliminar detalles no esenciales:** Por ejemplo, "Aparcó su coche grande y amarillo en la calle
        principal" -> "Aparcó su coche".
        2. **Transformar en ideas generales:** "Fui a la estación, compré un billete, esperé 20 minutos y subí
        al tren" -> "Cogí un tren".
    - **Variaciones según el propósito:**
        - Para un examen, la macroestructura puede ser más breve y centrada en los puntos clave.
        - Para una publicación, puede incluir más contexto para atraer al lector.
    - **Ejemplo práctico:**
        - Texto original: "María se levantó temprano, preparó café, leyó el periódico y salió a trabajar".
            - Macroestructura: "María comenzó su día y fue a trabajar".
        - Texto original: "El gobierno aprobó una ley que reduce los impuestos a las pequeñas empresas,
        lo que beneficiará a miles de emprendedores en el país".
            - Macroestructura: "El gobierno aprobó una ley para apoyar a las pequeñas empresas".

3. **Superestructura:**
    - **Deficinión:** Son las reglas o patrones que definen el género textual (narración, argumentación, 
    descripción, etc.), influyendo en la estructura y la finalidad del texto.
    - **Características:**
        - Determina qúe elementos son **obligatorios** (esenciales para cumplir la finalidad del género) y 
        cuáles son **opcionales** (pueden eliminarse sin afectar la esencia).
        - Por ejemplo, en una narración la superestructura incluye planteamiento, nudo y desenlace; en una carta
        formal, incluye saludo, cuerpo y despedida.
    - **Ejemplo práctico:**
        - **Género narrativo:** Una novela sigue la superestructura de planteamiento (presentación de personajes
        y contexto), nudo (conflicto principal) y desenlace (resolución). En *El principito*, el planteamiento
        es el encuentro del aviador con el principito, el nudo son sus aventuras, y el desenlace es su partida.
        - **Género argumentativo:** Un ensayo tiene una tesis (idea principal), argumentos (razones que la apoyan)
        y una conclusión. Por ejemplo, un ensayo sobre el cambio climático podría tener:
            - Tesis: "El cambio climático requiere acción inmediata".
            - Argumentos: Datos sobre el aumento de temperaturas, ejemplos de desastres naturales, citas de expertos.
            - Conclusión: "Debemos reducir las emisiones CO2".
        - **Género administrativo:** Una solicitud formal sigue una superestructura con saludo ("Estimado/a"), cuerpo
        (motivo de la solicitud) y despedida ("Atentamente").

## **IV. Importancia de los Niveles**

- **Microestructura:**
    - Es la base del contenido detallado, ya que incluye toda la información específica del texto.
    - Permite entender los detalles y las implicaciones del mensaje.
    - Ejemplo: En un cuento, la microestructura incluye las acciones específicas de los personajes ("El lobo
    se disfrazó de abuela").
- **Macroestructura:**
    - Es clave para resumir y comprender el texto, ya que condensa las ideas principales.
    - Ayuda a identificar el propósito del texto y a estudiarlo de forma eficiente.
    - Ejemplo: La macroestructura de un artículo sobre reciclaje podría ser: "El reciclaje reduce la 
    contaminación y ahorra recursos".
- **Superestructura:**
    - Guía la interpretación del texto al mostrar cómo está organizado según su género.
    - Ayuda a identificar la intención comunicativa (informar, persuadir, narrar).
    - Ejemplo: En un texto argumentativo, la superestructura permite reconocer la tesis y los argumentos,
    mientras que en una narración ayuda a seguir la secuencia de eventos.
""",
                1,
            ),
            (
                1,
                None,
                "Capítulo 2: Coherencia, cohesión y adecuación textuales",
                """
## **I. Introducción**

- **Propósito:** Este capítulo explica las tres propiedades esenciales que hacen que un texto sea
comunicativamente efectivo: **coherencia, cohesión y adecuación**.
- **Importancia:** Estas propiedades garantizan que un texto sea comprensible, unitario y apropiado para su
contexto, audiencia y propósito.
- **Ejemplo introductorio:** Un texto como "Voy a la tienda porque se acabó el pan" es coherente (tiene
sentido lógico), cohesionado (usa "porque" para conectar ideas) y adecuado (es un registro informal
apropiado para una conversación cotidiana).

## **II. Coherencia**

1. **Definición:** La coherencia es la propiedad que asegura que un texto remita a una realidad verosímil, ya
sea cotidiana, científica, literaria o ficticia, y que sus partes tengan sentido juntas.
    - Un texto coherente no presenta contradicciones internas y se ajusta a las expectativas del receptor.
2. **Condiciones de coherencia:**
    - Ejemplo:

""",
                1,
            ),
            (
                1,
                None,
                "Puntos clave: ¿Qué es un texto?",
                """
# Ecuaciones y esquemas
**Ecuación lineal:**
- Forma: $ax + b = 0$
- Solución: $x = -b/a$

**Ecuación cuadrática:**
- Forma: $ax^2 + bx + c = 0$
- Solución:
  $$x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$$

**Ejemplo práctico:**
Resolver $x^2 - 4x + 3 = 0$:
- $a = 1$, $b = -4$, $c = 3$
- Discriminante: $\\Delta = (-4)^2 - 4 \\cdot 1 \\cdot 3 = 16 - 12 = 4$
- Soluciones: $x = \\frac{4 \\pm \\sqrt{4}}{2} = \\frac{4 \\pm 2}{2}$, es decir, $x = 3$ o $x = 1$.
        """,
                1,
            ),
            (1, None, "Tema 2: Coherencia, cohesión y adecuación", "...", 1),
            (2, None, "Tema: La Guerra Civil Española", "Causas y consecuencias...", 1),
            (
                5,
                None,
                "ecuaciones",
                """
# Ecuaciones y esquemas
**Ecuación lineal:**
- Forma: $ax + b = 0$
- Solución: $x = -b/a$

**Ecuación cuadrática:**
- Forma: $ax^2 + bx + c = 0$
- Solución:
  $$x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$$

**Ejemplo práctico:**
Resolver $x^2 - 4x + 3 = 0$:
- $a = 1$, $b = -4$, $c = 3$
- Discriminante: $\\Delta = (-4)^2 - 4 \\cdot 1 \\cdot 3 = 16 - 12 = 4$
- Soluciones: $x = \\frac{4 \\pm \\sqrt{4}}{2} = \\frac{4 \\pm 2}{2}$, es decir, $x = 3$ o $x = 1$.
        """,
                1,
            ),
        ]
        cursor.executemany(
            "INSERT OR IGNORE INTO temas (asignatura_id, usuario_id, titulo, contenido, es_fijo) VALUES (?, ?, ?, ?, ?)",
            temas,
        )

        # Insertar exámenes
        examenes = [
            (1, "Práctica 1"),
            (2, "Historia 1"),
        ]
        cursor.executemany(
            "INSERT OR IGNORE INTO examenes (asignatura_id, nombre) VALUES (?, ?)",
            examenes,
        )

        # Insertar preguntas
        preguntas = [
            (1, "¿Qué es una oración simple?"),
            (1, "¿Qué tipo de oración es 'El gato duerme y el perro ladra'?"),
            (2, "¿Quiénes fueron los Reyes Católicos?"),
        ]
        cursor.executemany(
            "INSERT OR IGNORE INTO preguntas (examen_id, texto) VALUES (?, ?)",
            preguntas,
        )

        # Insertar opciones
        opciones = [
            (1, "Una oración con un solo predicado", 1),
            (1, "Una oración con dos predicados", 1),
            (1, "Una oración sin sujeto", 0),
            (1, "Una oración interrogativa", 0),
            (2, "Simple", 0),
            (2, "Compuesta", 1),
            (2, "Subordinada", 0),
            (2, "Exclamativa", 0),
            (3, "Isabel y Fernando", 1),
            (3, "Carlos I y Juana", 0),
            (3, "Felipe II y Ana", 0),
            (3, "Juan y María", 0),
        ]
        cursor.executemany(
            "INSERT OR IGNORE INTO opciones (pregunta_id, texto, es_correcta) VALUES (?, ?, ?)",
            opciones,
        )

        conn.commit()
    print("Base de datos inicializada con éxito.")
