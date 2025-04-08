import sqlite3
import os
from contextlib import closing
from werkzeug.security import generate_password_hash

# Ruta de la base de datos (coincide con app.py)
DB_PATH = "database.db"  # Cambiado de "database/uned_data.db" para coincidir con app.py

TABLES = {
    "usuarios": """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        );
    """,
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
            usuario_id INTEGER,
            titulo TEXT NOT NULL,
            contenido TEXT NOT NULL,
            es_fijo INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (asignatura_id) REFERENCES asignaturas(id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
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
            texto TEXT NOT NULL,  -- Cambiado "text" a "texto" para coincidir con app.py
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
    "intentos_examen": """
    CREATE TABLE IF NOT EXISTS intentos_examen (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        examen_id INTEGER,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        porcentaje_acierto REAL,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
        FOREIGN KEY (examen_id) REFERENCES examenes(id)
    );
    """,
}


def create_tables(cursor):
    for name, ddl in TABLES.items():
        cursor.execute(ddl)


def insert_initial_data(cursor):
    # Usuarios iniciales con contraseñas hasheadas
    usuarios = [
        ("usuario1", generate_password_hash("password1")),
        ("usuario2", generate_password_hash("password2")),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO usuarios (username, password) VALUES (?, ?)", usuarios
    )

    # Asignaturas (sin IDs explícitos, dejamos que SQLite los asigne)
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

    # Temas
    temas = [
        (
            1,  # asignatura_id (corresponde a "El comentario de texto")
            None,
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
            1,  # es_fijo
        ),
        (
            1,
            None,
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
        (1, None, "Tema 2: Coherencia, cohesión y adecuación", "...", 1),
        (2, None, "Tema: La Guerra Civil Española", "Causas y consecuencias...", 1),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO temas (asignatura_id, usuario_id, titulo, contenido, es_fijo) VALUES (?, ?, ?, ?, ?)",
        temas,
    )

    # Exámenes (sin IDs explícitos)
    examenes = [
        (1, "Práctica 1"),  # asignatura_id 1
        (2, "Historia 1"),  # asignatura_id 2
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO examenes (asignatura_id, titulo) VALUES (?, ?)",
        examenes,
    )

    # Preguntas (sin IDs explícitos)
    preguntas = [
        (1, "¿Qué es una oración simple?"),  # examen_id 1
        (1, "¿Qué tipo de oración es 'El gato duerme y el perro ladra'?"),
        (2, "¿Quiénes fueron los Reyes Católicos?"),  # examen_id 2
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO preguntas (examen_id, texto) VALUES (?, ?)",
        preguntas,
    )

    # Opciones
    opciones = [
        (1, "Una oración con un solo predicado", 1),
        (1, "Una oración con dos predicados", 0),
        (1, "Una oración sin sujeto", 0),  # Corregido: había un 1 duplicado
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
    # Crear el directorio si no existe (aunque ahora usamos database.db en la raíz)
    (
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        if os.path.dirname(DB_PATH)
        else None
    )
    with sqlite3.connect(DB_PATH) as conn:
        with closing(conn.cursor()) as cursor:
            create_tables(cursor)
            insert_initial_data(cursor)
        conn.commit()
    print("Base de datos inicializada con éxito.")


if __name__ == "__main__":
    init_db()
