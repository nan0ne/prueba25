"""
app.py - Aplicación web educativa con Flask

Descripción General:
Este archivo contiene la implementación de una aplicación web desarrollada con Flask
para gestionar asignaturas, temas y exámenes en un entorno educativo. Incluye autentificación
de usuarios, gestión de contenido y un sistema de evaluación con seguimiento de intentos.

Dependencias:
- Flask: Frameword web
- Flask-Login: Gestión de sesiones
- Werkzeug: Hashing de contraseñas
- SQLite: Base de datos (vía init_db.py)

Notas para producción:
1. Reemplazar 'tu_clave_secreta_aqui' por una clave segura.
2. Desactivar debug=True.
3. Consederar PostgreSQL para entornos de producción.
4. Asegurar HTTPS para SESSION_COOKIE_SECURE.
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from contextlib import closing
import socket
from init_db import init_db, get_db_connection
import markdown

# Inicialización de la aplicación Flask
app = Flask(__name__)
app.secret_key = (
    "tu_clave_secreta_aqui"  # Clave secreta para sesiones (cambiar en prod.)
)
app.config["SESSION_COOKIE_SECURE"] = True  # Requiere HTTPS para cookies
app.config["SESSION_COOKIE_HTTPONLY"] = True  # Protege cookies de JS
app.config["PERMANENT_SESSION_LIFETIME"] = 3600  # Sesiones expiran en 1 hora

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # Ruta de redirección para usuarios no aut.


class User(UserMixin):
    """Clase que representa un usuario aut.

    Hereda de UserMixin para compatibilidad con Flask-Login.

    Atributos:
        id (int): Identificador único del usuario.
        username (str): Nombre del usuario.
    """

    def __init__(self, id, username):
        self.id = id
        self.username = username


@login_manager.user_loader
def load_user(user_id):
    """Carga un usuario desde la base de datos basado en su ID.

    Args:
        user_id (str): ID del usuario a cargar.

    Returns:
        User | None: Instancia de User si existe, None si no.
    """
    with closing(get_db_connection()) as conn:
        user = conn.execute(
            "SELECT id, username FROM usuarios WHERE id = ?", (user_id,)
        ).fetchone()
        return User(user["id"], user["username"]) if user else None


def fetch_asignaturas():
    """Obtiene todas las asignaturas de la base de datos.

    Returns:
        list[dict]: Lista de diccionarios con id, nombre y descripción de cada asignatura.
    """
    with closing(get_db_connection()) as conn:
        return [
            dict(row)
            for row in conn.execute(
                "SELECT id, nombre, descripcion FROM asignaturas"
            ).fetchall()
        ]


def get_navbar_data():
    """Genera datos dinámicos para la barra de navegación.

    Returns:
        dict: Diccionario con estado de autenticación, nombre de usuario y modo oscuro.
    """
    return {
        "is_authenticated": current_user.is_authenticated,
        "username": current_user.username if current_user.is_authenticated else None,
        "dark_mode": session.get("dark_mode", False),
    }


@app.route("/")
def index():
    """Página principal que muestra todas las asignaturas.

    Returns:
        str: Plantilla renderizada con datos de navegación y asignaturas.
    """
    navbar_data = get_navbar_data()
    asignaturas = fetch_asignaturas()
    return render_template(
        "index.html", navbar_data=navbar_data, asignaturas=asignaturas
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    """Maneja el inicio de sesión de usuarios.

    Returns:
        str | Response: Plantilla de login o redirección al index si es exitoso.
    """
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username and password:
            with closing(get_db_connection()) as conn:
                user = conn.execute(
                    "SELECT id, username, password FROM usuarios WHERE username = ?",
                    (username,),
                ).fetchone()
                if user and check_password_hash(user["password"], password):
                    login_user(User(user["id"], user["username"]))
                    return redirect(url_for("index"))
                flash("Usuario o contraseña incorrectos", "danger")
    return render_template(
        "login.html", asignaturas=fetch_asignaturas(), navbar_data=get_navbar_data()
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    """Maneja el registro de nuevos usuarios.

    Returns:
        str | Response: Plantilla de registro o redirección al login si es exitoso.
    """
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not (
            username
            and password
            and len(username) >= 4
            and len(password) >= 8
            and username.isalnum()
        ):
            flash(
                "Usuario: mínimo 4 caracteres alfanuméricos. Contraseña: mínimo 8 caracteres.",
                "danger",
            )
        else:
            with closing(get_db_connection()) as conn:
                if conn.execute(
                    "SELECT 1 FROM usuarios WHERE username = ?", (username,)
                ).fetchone():
                    flash("El usuario ya existe.", "danger")
                else:
                    hashed_password = generate_password_hash(password)
                    conn.execute(
                        "INSERT INTO usuarios (username, password) VALUES (?, ?)",
                        (username, hashed_password),
                    )
                    conn.commit()
                    flash("Registro exitoso. Por favor, inicia sesión.", "success")
                    return redirect(url_for("login"))
    return render_template(
        "register.html", asignaturas=fetch_asignaturas(), navbar_data=get_navbar_data()
    )


@app.route("/logout")
@login_required
def logout():
    """Cierra la sesión del usuario actual.

    Returns:
        Response: Redirección al index.
    """
    logout_user()
    return redirect(url_for("index"))


@app.route("/asignatura/<int:asignatura_id>")
def mostrar_asignatura(asignatura_id):
    """Muestra el menú de una asignatura específica.

    Args:
        asignatura_id (int): ID de la asignatura.

    Returns:
        str | Response: Plantilla renderizada o redirección al index si no existe.
    """
    with closing(get_db_connection()) as conn:
        asignatura = conn.execute(
            "SELECT id, nombre FROM asignaturas WHERE id = ?", (asignatura_id,)
        ).fetchone()
        if not asignatura:
            return redirect(url_for("index"))
    return render_template(
        "asignatura_menu.html",
        asignatura=dict(asignatura),
        asignaturas=fetch_asignaturas(),
        navbar_data=get_navbar_data(),
    )


@app.route("/asignatura/<int:asignatura_id>/temas")
def mostrar_temas(asignatura_id):
    """Muestra los temas de una asignatura.

    Args:
        asignatura_id (int): ID de la asignatura.

    Returns:
        str | Response: Plantilla renderizada con temas o redirección al index.
    """
    with closing(get_db_connection()) as conn:
        asignatura_row = conn.execute(
            "SELECT id, nombre FROM asignaturas WHERE id = ?", (asignatura_id,)
        ).fetchone()
        if not asignatura_row:
            return redirect(url_for("index"))
        asignatura = dict(asignatura_row)
        temas = [
            {
                "id": row["id"],
                "titulo": row["titulo"],
                "contenido": markdown.markdown(
                    row["contenido"], extensions=["extra", "fenced_code"]
                ),
                "usuario_id": row["usuario_id"],
                "es_fijo": row["es_fijo"],
            }
            for row in conn.execute(
                "SELECT id, titulo, contenido, usuario_id, es_fijo FROM temas WHERE asignatura_id = ? ORDER BY id ASC",
                (asignatura_id,),
            ).fetchall()
        ]
    return render_template(
        "temas.html",
        asignatura=asignatura,
        temas=temas,
        asignaturas=fetch_asignaturas(),
        navbar_data=get_navbar_data(),
    )


@app.route("/asignatura/<int:asignatura_id>/agregar_tema", methods=["GET", "POST"])
@login_required
def agregar_tema(asignatura_id):
    """Permite agregar un nuevo tema a una asignatura.

    Args:
        asignatura_id (int): ID de la asignatura.

    Returns:
        str | Response: Plantilla de agregar tema o redirección tras éxito.
    """
    with closing(get_db_connection()) as conn:
        asignatura_row = conn.execute(
            "SELECT id, nombre FROM asignaturas WHERE ID = ?", (asignatura_id,)
        ).fetchone()
        if not asignatura_row:
            return redirect(url_for("index"))
        asignatura = dict(asignatura_row)
    if request.method == "POST":
        titulo = request.form.get("titulo")
        contenido = request.form.get("contenido")
        if titulo and contenido:
            with closing(get_db_connection()) as conn:
                conn.execute(
                    "INSERT INTO temas (asignatura_id, usuario_id, titulo, contenido, es_fijo) VALUES (?, ?, ?, ?, ?)",
                    (asignatura_id, current_user.id, titulo, contenido, 0),
                )
                conn.commit()
                flash("Tema agregado con éxito.", "success")
                return redirect(url_for("mostrar_temas", asignatura_id=asignatura_id))
        flash("Titulo y contenido son obligatorios.", "danger")
    return render_template(
        "agregar_tema.html",
        asignatura_id=asignatura_id,
        asignatura=asignatura,
        asignaturas=fetch_asignaturas(),
        navbar_data=get_navbar_data(),
    )


@app.route(
    "/asignatura/<int:asignatura_id>/editar_tema/<int:tema_id>", methods=["GET", "POST"]
)
@login_required
def editar_tema(asignatura_id, tema_id):
    """Permite editar un tema existente.

    Args:
        asignatura_id(int): ID de la asignatura.
        tema_id(int): ID del tema a editar.

    Returns:
        str | Response: Plantilla de edición o redirección tras éxito.
    """
    with closing(get_db_connection()) as conn:
        asignatura_row = conn.execute(
            "SELECT id, nombre FROM asignaturas WHERE id = ?", (asignatura_id,)
        ).fetchone()
        tema_row = conn.execute(
            "SELECT id, asignatura_id, usuario_id, titulo, contenido, es_fijo FROM temas WHERE id = ? AND asignatura_id = ?",
            (tema_id, asignatura_id),
        ).fetchone()
        if not asignatura_row or not tema_row:
            return redirect(url_for("index"))
        asignatura = dict(asignatura_row)
        tema = dict(tema_row)
        if tema["usuario_id"] != current_user.id or tema["es_fijo"] == 1:
            flash("No tienes permiso para editar este tema." "danger")
            return redirect(url_for("mostrar_temas", asignatura_id=asignatura_id))
    if request.method == "POST":
        titulo = request.form.get("titulo")
        contenido = request.form.get("contenido")
        if titulo and contenido:
            with closing(get_db_connection()) as conn:
                conn.execute(
                    "UPDATE temas SET titulo = ?, contenido = ? WHERE id = ? AND usuario_id = ?",
                    (titulo, contenido, tema_id, current_user.id),
                )
                conn.commit()
                flash("Tema actualizado con éxito.", "success")
                return redirect(url_for("mostrar_temas", asignatura_id=asignatura_id))
        flash("Título y contenido son obligatorios.", "danger")
    return render_template(
        "editar_tema.html",
        asignatura_id=asignatura_id,
        asignatura=asignatura,
        tema=tema,
        asignaturas=fetch_asignaturas(),
        navbar_data=get_navbar_data(),
    )


@app.route(
    "/asignatura/<int:asignatura_id>/eliminar_tema/<int:tema_id>", methods=["POST"]
)
@login_required
def eliminar_tema(asignatura_id, tema_id):
    """Elimina un tema existente.

    Args:
        asignatura_id (int): ID de la asignatura.
        tema_id (int): ID del tema a eliminar.

    Returns:
        Response: Redirección a la lista de temas.
    """
    with closing(get_db_connection()) as conn:
        tema_row = conn.execute(
            "SELECT  usuario_id, es_fijo FROM temas WHERE id = ? AND asignatura_id = ?",
            (tema_id, asignatura_id),
        ).fetchone()
        if not tema_row or (
            tema_row["usuario_id"] != current_user.id or tema_row["es_fijo"] == 1
        ):
            flash("No tienes permiso para eliminar este tema.", "danger")
        else:
            conn.execute(
                "DELETE FROM temas WHERE id = ? AND usuario_id = ?",
                (tema_id, current_user.id),
            )
            conn.commit()
            flash("Tema eliminado con éxito.", "success")
    return redirect(url_for("mostrar_temas", asignatura_id=asignatura_id))


@app.route("/asignatura/<int:asignatura_id>/examenes")
def mostrar_examenes(asignatura_id):
    """Muestra los exámenes de una asignatura.

    Args:
        asignatura_id (int): ID de la asignatura.

    Returns:
        str | Response: Plantilla renderizada con exámenes.
    """
    with closing(get_db_connection()) as conn:
        asignatura_row = conn.execute(
            "SELECT id, nombre FROM asignaturas WHERE id = ?", (asignatura_id,)
        ).fetchone()
        if not asignatura_row:
            return redirect(url_for("index"))
        asignatura = dict(asignatura_row)
        examenes = [
            dict(row)
            for row in conn.execute(
                "SELECT id, nombre FROM examenes WHERE asignatura_id = ?",
                (asignatura_id,),
            ).fetchall()
        ]
    return render_template(
        "examenes.html",
        asignatura=asignatura,
        examenes=examenes,
        asignaturas=fetch_asignaturas(),
        navbar_data=get_navbar_data(),
    )


@app.route("/examen/<int:examen_id>", methods=["GET", "POST"])
@login_required
def mostrar_examen(examen_id):
    """Muestra y procesa un examen.

    Args:
        examen_id (int): ID del examen.

    Returns:
        str | Response: Plantilla con examen o resultados tras envío.
    """
    with closing(get_db_connection()) as conn:
        examen_row = conn.execute(
            "SELECT id, nombre, asignatura_id FROM examenes WHERE id = ?", (examen_id,)
        ).fetchone()
        if not examen_row:
            return redirect(url_for("index"))
        examen = dict(examen_row)
        preguntas = [
            dict(row)
            for row in conn.execute(
                "SELECT id, texto FROM preguntas WHERE examen_id = ?", (examen_id,)
            ).fetchall()
        ]
        for pregunta in preguntas:
            pregunta["opciones"] = [
                dict(row)
                for row in conn.execute(
                    "SELECT id, texto, es_correcta FROM opciones WHERE pregunta_id = ?",
                    (pregunta["id"],),
                ).fetchall()
            ]
        examen["preguntas"] = preguntas

        intentos = [
            dict(row)
            for row in conn.execute(
                """
                SELECT id, porcentaje_acierto, respuestas_correctas, respuestas_incorrectas, 
                fecha FROM intentos_examen
                WHERE usuario_id = ? AND examen_id = ?
                ORDER BY fecha DESC
                """,
                (current_user.id, examen_id),
            ).fetchall()
        ]

        if request.method == "POST":
            resultado = []
            total_correctas = 0  # Total de opciones correctas en el examen
            aciertos = 0  # Opciones correctas seleccionadas
            fallos = 0  # Opciones incorrectas seleccionadas

            for pregunta in examen["preguntas"]:
                seleccionadas = request.form.getlist(f"pregunta_{pregunta['id']}")
                seleccionadas = [int(s) for s in seleccionadas]
                correctas = [
                    opcion["id"]
                    for opcion in pregunta["opciones"]
                    if opcion["es_correcta"]
                ]
                total_correctas += len(correctas)

                # Contar aciertos y fallos por pregunta
                aciertos_pregunta = sum(1 for c in correctas if c in seleccionadas)
                fallos_pregunta = sum(1 for s in seleccionadas if s not in correctas)
                aciertos += aciertos_pregunta
                fallos += fallos_pregunta

                resultado.append(
                    {
                        "texto": pregunta["texto"],
                        "opciones": pregunta["opciones"],
                        "seleccionadas": seleccionadas,
                        "correctas": correctas,
                        "aciertos": aciertos_pregunta,
                        "fallos": fallos_pregunta,
                        "total_correctas": len(correctas),
                    }
                )

            # Calcular porcentaje: (aciertos / total_correctas) * 100
            porcentaje_acierto = (
                (aciertos / total_correctas) * 100 if total_correctas > 0 else 0
            )
            porcentaje_acierto = round(porcentaje_acierto, 2)

            conn.execute(
                """
                INSERT INTO intentos_examen (
                    usuario_id, examen_id, porcentaje_acierto, respuestas_correctas, respuestas_incorrectas
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    current_user.id,
                    examen_id,
                    porcentaje_acierto,
                    aciertos,
                    fallos,
                ),
            )
            conn.commit()
            return render_template(
                "examen.html",
                examen=examen,
                resultado=resultado,
                porcentaje_acierto=porcentaje_acierto,
                intentos=fetch_intentos(examen_id),
                navbar_data=get_navbar_data(),
            )
        return render_template(
            "examen.html",
            examen=examen,
            intentos=fetch_intentos(examen_id),
            navbar_data=get_navbar_data(),
        )


def fetch_intentos(examen_id):
    """OBtiene los intentos de un usuario en un examen.

    Args:
        examen_id (int): ID del examen.

    Returns:
        list[dict]: Lista de intentos con porcentaje, aciertos, fallos y fecha.
    """
    with closing(get_db_connection()) as conn:
        intentos = [
            dict(row)
            for row in conn.execute(
                """
                SELECT id, porcentaje_acierto, respuestas_correctas, respuestas_incorrectas, fecha
                FROM intentos_examen
                WHERE usuario_id = ? AND examen_id = ?
                ORDER BY fecha DESC
                """,
                (current_user.id, examen_id),
            ).fetchall()
        ]
    return intentos


@app.route("/examen/<int:examen_id>/resetear_intentos", methods=["POST"])
@login_required
def resetear_intentos(examen_id):
    """Resetea los intentos de un usuario en un examen.

    Args:
        examen_id (int): ID del examen.

    Returns:
        Response: Redirección al examen.
    """
    with closing(get_db_connection()) as conn:
        conn.execute(
            "DELETE FROM intentos_examen WHERE usuario_id = ? AND examen_id = ?",
            (current_user.id, examen_id),
        )
        conn.commit()
    flash("Registro de intentos reseteado con éxito.", "success")
    return redirect(url_for("mostrar_examen", examen_id=examen_id))


@app.route("/toggle_theme", methods=["POST"])
def toggle_theme():
    """Alterna entre modo claro y oscuro.

    Returns:
        Response: Redirección a la página anterior o al index.
    """
    session["dark_mode"] = not session.get("dark_mode", False)
    return redirect(request.referrer or url_for("index"))


def find_free_port(start_port=5000):
    """Encuentra un puerto libre para ejecutar el servidor.

    Args:
        start_port (int): Puerto inicial a probar. Por defecto 5000.

    Returns:
        int: Puerto libre encontrado.
    """
    port = start_port
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("0.0.0.0", port))
                return port
            except OSError:
                port += 1


if __name__ == "__main__":
    """Ejecuta la aplicación en modo desarrolo."""
    with app.app_context():
        init_db()  # Inicializa la base de datos
    port = find_free_port(5000)
    print(f"Starting server on port{port}...")
    app.run(debug=True, host="0.0.0.0", port=port)  # Modo debug para desarrollo
