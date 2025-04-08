# import sqlite3
# import os
# from contextlib import closing

# DB_PATH = "database/uned_data.db"

# TABLES = {
#     "asignaturas": """
#         CREATE TABLE IF NOT EXISTS asignaturas (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             nombre TEXT NOT NULL,
#             descripcion TEXT
#         );
#     """,
#     "resumenes": """
#         CREATE TABLE IF NOT EXISTS resumenes (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             asignatura_id INTEGER,
#             titulo TEXT NOT NULL,
#             contenido TEXT NOT NULL,
#             es_fijo INTEGER NOT NULL DEFAULT 0,
#             FOREIGN KEY (asignatura_id) REFERENCES asignaturas(id)
#         );
#     """,
#     "examenes": """
#         CREATE TABLE IF NOT EXISTS examenes (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             asignatura_id INTEGER,
#             titulo TEXT NOT NULL,
#             FOREIGN KEY (asignatura_id) REFERENCES asignaturas(id)
#         );
#     """,
#     "preguntas": """
#         CREATE TABLE IF NOT EXISTS preguntas (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             examen_id INTEGER,
#             text TEXT NOT NULL,
#             FOREIGN KEY (examen_id) REFERENCES examenes(id)
#         );
#     """,
#     "opciones": """
#         CREATE TABLE IF NOT EXISTS opciones (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             pregunta_id INTEGER,
#             texto TEXT NOT NULL,
#             es_correcta INTEGER NOT NULL,
#             FOREIGN KEY (pregunta_id) REFERENCES preguntas(id)
#         );
#     """,
# }


# def create_tables(cursor):
#     for name, ddl in TABLES.items():
#         cursor.execute(ddl)


# def insert_initial_data(cursor):
#     asignaturas = [
#         (1, "El comentario de texto", "Teoría y práctica"),
#         (2, "Lengua Española", "Manual de lengua Española"),
#         (3, "Inglés", "Curso de Inglés para adultos"),
#         (4, "Informática", "Introducción a la informática básica"),
#         (5, "Matemáticas", "Volumen 1 y volumen 2"),
#     ]
#     cursor.executemany(
#         "INSERT OR IGNORE INTO asignaturas (id, nombre, descripcion) VALUES (?, ?, ?)",
#         asignaturas,
#     )

#     """
#     Uso \n para saltos de línea.
#     Uso Markdown (# para títulos, - para listas, ** para negritas) para estructurar el contenido.
#     Esto se almacena como texto plano en contenido.
#     """
#     resumenes = [
#         (
#             1,  # asignatura_id
#             "Resumen Capítulo 1: ¿Qué es un texto?",
#             """
# # Resumen del Tema 1: ¿Qué es un texto?
# Un texto es un acto de comunicación mediante el cual se transmite un mensaje
# coherente y autónomo entre un emisor y un receptor, ya sea de forma oral o escrita.
# No depende de su extensión, sino de su capacidad para transmitir un mensaje interpretable,
# como se ve en ejemplos simples ("¡Socorro!") o complejos (novelas, ensayos).
# El texto se compone de tres elementos principales:
# - **Emisor**: Individual o colectivo, cuya perspectiva temporal y espacial influye en el mensaje.
# - **Receptor**: Específico o genérico, como en textos literarios o carteles públicos.
# - **Mensaje**: El contenido transmitido, que varía en complejidad.
# La interpretación adecuada del texto requiere considerar estas coordenadas.
# Además, los textos se organizan en tres niveles:
# - **1. Microestructura**: El contenido detallado y explícito, incluyendo información implícita derivada del contexto.
# - **2. Macroestructura**: Un resumen que condensa las ideas esenciales, simplificando o eliminando detalles secundarios,
#   con variaciones según el propósito (e.g., examen o publicación).
# - **3. Superestructura**: Las reglas que definen el género textual (narración, argumentación, etc.),
#   influyendo en su finalidad y en qué contenidos son prioritarios para la macroestructura.
# Comprender estos niveles permite analizar y resumir textos de manera efectiva, identificando su intención y estructura.
#             """,
#             1,  # es_fijo
#         ),
#         (
#             1,  # asignatura_id para Lengua Castellana
#             "Esquema capítulo 1: ¿Qué es un texto?",
#             """
# # Esquema del Tema 1: ¿Qué es un texto?
# ## I. Definición de Texto
# - **Concepto**: Acto de comunicación que transmite un mensaje coherente y autónomo.
# - **Características**:
#   - Puede ser oral o escrito.
#   - No depende de la extensión, sino de la capacidad de transmitir un mensaje interpretable.
# - **Ejemplos**:
#   - Simples: "¡Socorro!" o "¡Qué alguien me ayude!".
#   - Complejos: Novelas, noticias, ensayos.
# ## II. Constituyentes del Texto
# - **Emisor o productor**:
#   - Individuo o colectivo (e.g., Asamblea Constituyente).
#   - Influye en el texto según su tiempo (momento de emisión) y lugar (espacio de producción).
#   - Ejemplo: "Nos veremos mañana" (interpretable según el día de emisión).
# - **Receptor o Destinatario**:
#   - **Específico**: Identidad conocida.
#             """,
#             1,  # es_fijo
#         ),
#         (
#             1,
#             "Resumen Capítulo 2: Coherencia, cohesión y adecuación textuales.",
#             """...""",
#             1,
#         ),
#         (
#             1,
#             "Esquema Capítulo 2: Coherencia, cohesión y adecuación textuales.",
#             """...""",
#             1,
#         ),
#         (
#             2,
#             "Resumen de la Guerra civil",
#             "Causas y consecuencias de la Guerra Civil Espanola... ",
#             1,
#         ),
#     ]
#     cursor.executemany(
#         "INSERT OR IGNORE INTO resumenes (asignatura_id, titulo, contenido, es_fijo) VALUES (?, ? , ?, ?)",
#         resumenes,
#     )

#     examenes = [(1, 1, "Examen de Practica 1"), (2, 2, "Examen de Historia 1")]
#     cursor.executemany(
#         "INSERT OR IGNORE INTO examenes (id, asignatura_id, titulo) VALUES (?, ?, ?)",
#         examenes,
#     )

#     preguntas = [
#         (1, 1, "Que es una oracion simple?"),
#         (2, 1, 'Que tipo de oracion es "El gato duerme y el perro ladra"?'),
#         (3, 2, "Quienes fueron los Reyes Catolicos?"),
#     ]
#     cursor.executemany(
#         "INSERT OR IGNORE INTO preguntas (id, examen_id, text) VALUES (?, ?, ?)",
#         preguntas,
#     )

#     opciones = [
#         # Pregunta 1
#         (1, "Una oracion con un solo predicado", 1),
#         (1, "Una oracion con dos predicados", 0),
#         (1, "Una oracion sin sujeto", 1),
#         (1, "Una oracion interrogativa", 0),
#         # Pregunta 2
#         (2, "Simple", 0),
#         (2, "Compuesta", 1),
#         (2, "Subordinada", 0),
#         (2, "Exclamativa", 0),
#         # Pregunta 3
#         (3, "Isabel y Fernando", 1),
#         (3, "Carlos I y Juana", 0),
#         (3, "Felipe II y Ana", 0),
#         (3, "Juan y Maria", 0),
#     ]
#     cursor.executemany(
#         "INSERT OR IGNORE INTO opciones (pregunta_id, texto, es_correcta) VALUES (?, ?, ?)",
#         opciones,
#     )


# def init_db():
#     os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
#     with sqlite3.connect(DB_PATH) as conn:
#         with closing(conn.cursor()) as cursor:
#             create_tables(cursor)
#             insert_initial_data(cursor)
#         conn.commit()
#     print("Base de datos inicializada con exito.")


# if __name__ == "__main__":
#     init_db()
import sqlite3
import os
from contextlib import closing

DB_PATH = "database/uned_data.db"

TABLES = {
    "asignaturas": """
        CREATE TABLE IF NOT EXISTS asignaturas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT
        );
    """,
    "temas": """
        CREATE TABLE IF NOT EXISTS temas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asignatura_id INTEGER,
            titulo TEXT NOT NULL,
            contenido TEXT NOT NULL,
            es_fijo INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (asignatura_id) REFERENCES asignaturas(id)
        );
    """,
    "examenes": """
        CREATE TABLE IF NOT EXISTS examenes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asignatura_id INTEGER,
            titulo TEXT NOT NULL,
            FOREIGN KEY (asignatura_id) REFERENCES asignaturas(id)
        );
    """,
    "preguntas": """
        CREATE TABLE IF NOT EXISTS preguntas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            examen_id INTEGER,
            text TEXT NOT NULL,
            FOREIGN KEY (examen_id) REFERENCES examenes(id)
        );
    """,
    "opciones": """
        CREATE TABLE IF NOT EXISTS opciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pregunta_id INTEGER,
            texto TEXT NOT NULL,
            es_correcta INTEGER NOT NULL,
            FOREIGN KEY (pregunta_id) REFERENCES preguntas(id)
        );
    """,
}


import sqlite3
import os
from contextlib import closing

DB_PATH = "database/uned_data.db"

TABLES = {
    "asignaturas": """
        CREATE TABLE IF NOT EXISTS asignaturas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT
        );
    """,
    "temas": """
        CREATE TABLE IF NOT EXISTS temas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asignatura_id INTEGER,
            titulo TEXT NOT NULL,
            contenido TEXT NOT NULL,
            es_fijo INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (asignatura_id) REFERENCES asignaturas(id)
        );
    """,
    "examenes": """
        CREATE TABLE IF NOT EXISTS examenes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asignatura_id INTEGER,
            titulo TEXT NOT NULL,
            FOREIGN KEY (asignatura_id) REFERENCES asignaturas(id)
        );
    """,
    "preguntas": """
        CREATE TABLE IF NOT EXISTS preguntas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            examen_id INTEGER,
            text TEXT NOT NULL,
            FOREIGN KEY (examen_id) REFERENCES examenes(id)
        );
    """,
    "opciones": """
        CREATE TABLE IF NOT EXISTS opciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pregunta_id INTEGER,
            texto TEXT NOT NULL,
            es_correcta INTEGER NOT NULL,
            FOREIGN KEY (pregunta_id) REFERENCES preguntas(id)
        );
    """,
}


def create_tables(cursor):
    for name, ddl in TABLES.items():
        cursor.execute(ddl)


def insert_initial_data(cursor):
    asignaturas = [
        (1, "El comentario de texto", "Teoría y práctica"),
        (2, "Lengua Española", "Manual de lengua Española"),
        (3, "Inglés", "Curso de Inglés para adultos"),
        (4, "Informática", "Introducción a la informática básica"),
        (5, "Matemáticas", "Volumen 1 y volumen 2"),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO asignaturas (id, nombre, descripcion) VALUES (?, ?, ?)",
        asignaturas,
    )

    temas = [
        (
            1,
            "Tema 1: ¿Qué es un texto?",
            """
# Tema 1: ¿Qué es un texto?
Un texto es un acto de comunicación que transmite un mensaje coherente y autónomo entre un emisor y un receptor, ya sea oral o escrito. No depende de su extensión, sino de su capacidad para ser interpretable (e.g., "¡Socorro!" o una novela).  
**Componentes clave:**
- **Emisor**: Individuo o colectivo, influido por su tiempo y espacio.
- **Receptor**: Específico o genérico.
- **Mensaje**: Contenido variable en complejidad.  
**Niveles de análisis:**
1. **Microestructura**: Detalles explícitos e implícitos.
2. **Macroestructura**: Resumen de ideas esenciales.
3. **Superestructura**: Reglas del género textual (narración, argumentación, etc.).
            """,
            1,
        ),
        (
            1,
            "Puntos clave: ¿Qué es un texto?",
            """
# Puntos clave: ¿Qué es un texto?
- **Definición**: Comunicación coherente y autónoma.
- **Tipos**: Oral o escrito; simple ("¡Socorro!") o complejo (ensayos).
- **Elementos**:
  - Emisor: Perspectiva temporal-espacial.
  - Receptor: Conocido o público general.
  - Mensaje: Interpretable.
- **Estructura**:
  - Micro: Detalles.
  - Macro: Ideas principales.
  - Super: Género textual.
            """,
            1,
        ),
        (
            1,
            "Tema 2: Coherencia, cohesión y adecuación",
            """...""",
            1,
        ),
        (
            1,
            "Puntos clave: Coherencia, cohesión y adecuación",
            """...""",
            1,
        ),
        (
            2,
            "Tema: La Guerra Civil Española",
            "Causas y consecuencias de la Guerra Civil Española...",
            1,
        ),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO temas (asignatura_id, titulo, contenido, es_fijo) VALUES (?, ?, ?, ?)",
        temas,
    )

    examenes = [(1, 1, "Práctica 1"), (2, 2, "Historia 1")]
    cursor.executemany(
        "INSERT OR IGNORE INTO examenes (id, asignatura_id, titulo) VALUES (?, ?, ?)",
        examenes,
    )

    preguntas = [
        (1, 1, "¿Qué es una oración simple?"),
        (2, 1, "¿Qué tipo de oración es 'El gato duerme y el perro ladra'?"),
        (3, 2, "¿Quiénes fueron los Reyes Católicos?"),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO preguntas (id, examen_id, text) VALUES (?, ?, ?)",
        preguntas,
    )

    opciones = [
        (1, "Una oración con un solo predicado", 1),
        (1, "Una oración con dos predicados", 0),
        (1, "Una oración sin sujeto", 1),
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


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        with closing(conn.cursor()) as cursor:
            create_tables(cursor)
            insert_initial_data(cursor)
        conn.commit()
    print("Base de datos inicializada con éxito.")


if __name__ == "__main__":
    init_db()
