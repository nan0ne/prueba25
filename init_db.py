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
## **I Definición de Texto**

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
        - Un artículo científico que explica un experimento con datos y análisis detallados.
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
