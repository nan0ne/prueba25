import sqlite3
from contextlib import closing
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash
import socket
from datetime import datetime

app = Flask(__name__)
app.secret_key = "tu_clave_secreta_aqui"
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = 3600

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username


@login_manager.user_loader
def load_user(user_id):
    with closing(get_db_connection()) as conn:
        user = conn.execute(
            "SELECT * FROM usuarios WHERE id = ?", (user_id,)
        ).fetchone()
        return User(user["id"], user["username"]) if user else None


def get_db_connection():
    conn = sqlite3.connect("database.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with closing(get_db_connection()) as conn:
        # Crear la tabla si no existe
        conn.execute(
            """CREATE TABLE IF NOT EXISTS intentos_examen (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            examen_id INTEGER,
            porcentaje_acierto REAL,
            fecha TEXT,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
            FOREIGN KEY (examen_id) REFERENCES examenes(id)
        )"""
        )
        # Añadir columnas nuevas si no existen
        try:
            conn.execute(
                "ALTER TABLE intentos_examen ADD COLUMN respuestas_correctas INTEGER DEFAULT 0"
            )
        except sqlite3.OperationalError:
            pass  # Ignorar si ya existe
        try:
            conn.execute(
                "ALTER TABLE intentos_examen ADD COLUMN respuestas_incorrectas INTEGER DEFAULT 0"
            )
        except sqlite3.OperationalError:
            pass  # Ignorar si ya existe
        conn.commit()


def get_asignaturas():
    with closing(get_db_connection()) as conn:
        return [
            dict(row) for row in conn.execute("SELECT * FROM asignaturas").fetchall()
        ]


def get_navbar_data():
    return {
        "is_authenticated": current_user.is_authenticated,
        "username": current_user.username if current_user.is_authenticated else None,
        "dark_mode": session.get("dark_mode", False),
    }


@app.route("/")
def index():
    return render_template(
        "index.html", asignaturas=get_asignaturas(), navbar_data=get_navbar_data()
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username and password:
            with closing(get_db_connection()) as conn:
                user = conn.execute(
                    "SELECT * FROM usuarios WHERE username = ?", (username,)
                ).fetchone()
                if user and check_password_hash(user["password"], password):
                    login_user(User(user["id"], user["username"]))
                    return redirect(url_for("index"))
                flash("Usuario o contraseña incorrectos", "danger")
    return render_template(
        "login.html", asignaturas=get_asignaturas(), navbar_data=get_navbar_data()
    )


@app.route("/register", methods=["GET", "POST"])
def register():
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
                "El usuario debe tener al menos 4 caracteres alfanuméricos y la contraseña 8 caracteres.",
                "danger",
            )
        else:
            with closing(get_db_connection()) as conn:
                if conn.execute(
                    "SELECT * FROM usuarios WHERE username = ?", (username,)
                ).fetchone():
                    flash("El usuario ya existe.", "danger")
                else:
                    hashed_password = generate_password_hash(password)
                    conn.execute(
                        "INSERT INTO usuarios (username, password) VALUES (?, ?)",
                        (username, hashed_password),
                    )
                    conn.commit()
                    return redirect(url_for("login"))
    return render_template(
        "register.html", asignaturas=get_asignaturas(), navbar_data=get_navbar_data()
    )


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/asignatura/<int:asignatura_id>")
def mostrar_asignatura(asignatura_id):
    with closing(get_db_connection()) as conn:
        asignatura = conn.execute(
            "SELECT * FROM asignaturas WHERE id = ?", (asignatura_id,)
        ).fetchone()
        if not asignatura:
            return redirect(url_for("index"))
    return render_template(
        "asignatura_menu.html",
        asignatura=asignatura,
        asignaturas=get_asignaturas(),
        navbar_data=get_navbar_data(),
    )


@app.route("/asignatura/<int:asignatura_id>/temas")
def mostrar_temas(asignatura_id):
    with closing(get_db_connection()) as conn:
        asignatura = conn.execute(
            "SELECT * FROM asignaturas WHERE id = ?", (asignatura_id,)
        ).fetchone()
        if not asignatura:
            return redirect(url_for("index"))
        temas = [
            dict(row)
            for row in conn.execute(
                "SELECT * FROM temas WHERE asignatura_id = ?", (asignatura_id,)
            ).fetchall()
        ]
    return render_template(
        "temas.html",
        asignatura=asignatura,
        temas=temas,
        asignaturas=get_asignaturas(),
        navbar_data=get_navbar_data(),
    )


@app.route("/asignatura/<int:asignatura_id>/examenes")
def mostrar_examenes(asignatura_id):
    with closing(get_db_connection()) as conn:
        asignatura = conn.execute(
            "SELECT * FROM asignaturas WHERE id = ?", (asignatura_id,)
        ).fetchone()
        if not asignatura:
            return redirect(url_for("index"))
        examenes = [
            dict(row)
            for row in conn.execute(
                "SELECT * FROM examenes WHERE asignatura_id = ?", (asignatura_id,)
            ).fetchall()
        ]
    return render_template(
        "examenes.html",
        asignatura=asignatura,
        examenes=examenes,
        asignaturas=get_asignaturas(),
        navbar_data=get_navbar_data(),
    )


@app.route("/examen/<int:examen_id>", methods=["GET", "POST"])
@login_required
def mostrar_examen(examen_id):
    with closing(get_db_connection()) as conn:
        examen = conn.execute(
            "SELECT * FROM examenes WHERE id = ?", (examen_id,)
        ).fetchone()
        if not examen:
            return redirect(url_for("index"))
        examen = dict(examen)
        preguntas = [
            dict(row)
            for row in conn.execute(
                "SELECT * FROM preguntas WHERE examen_id = ?", (examen_id,)
            ).fetchall()
        ]
        for pregunta in preguntas:
            pregunta["opciones"] = [
                dict(row)
                for row in conn.execute(
                    "SELECT * FROM opciones WHERE pregunta_id = ?", (pregunta["id"],)
                ).fetchall()
            ]
            pregunta["respuestas_correctas"] = [
                op["id"] for op in pregunta["opciones"] if op["es_correcta"]
            ]
        examen["preguntas"] = preguntas
        intentos = [
            dict(row)
            for row in conn.execute(
                "SELECT * FROM intentos_examen WHERE usuario_id = ? AND examen_id = ? ORDER BY fecha DESC LIMIT 10",
                (current_user.id, examen_id),
            ).fetchall()
        ]

    resultado = None
    porcentaje_acierto = None
    if request.method == "POST":
        respuestas_usuario = {}
        for key, values in request.form.lists():
            if key.startswith("pregunta_"):
                pregunta_id = int(key.split("_")[1])
                respuestas_usuario[pregunta_id] = [
                    int(v) for v in values if v.isdigit()
                ]

        total_preguntas = len(examen["preguntas"])
        aciertos = 0
        resultado = []
        for pregunta in examen["preguntas"]:
            correctas = set(pregunta["respuestas_correctas"])
            seleccionadas = set(respuestas_usuario.get(pregunta["id"], []))
            es_correcta = correctas == seleccionadas
            if es_correcta:
                aciertos += 1
            resultado.append(
                {
                    "texto": pregunta["texto"],
                    "opciones": pregunta["opciones"],
                    "correctas": correctas,
                    "seleccionadas": seleccionadas,
                    "es_correcta": es_correcta,
                }
            )

        porcentaje_acierto = (
            (aciertos / total_preguntas) * 100 if total_preguntas > 0 else 0
        )
        respuestas_incorrectas = total_preguntas - aciertos
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with closing(get_db_connection()) as conn:
            conn.execute(
                "INSERT INTO intentos_examen (usuario_id, examen_id, porcentaje_acierto, respuestas_correctas, respuestas_incorrectas, fecha) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    current_user.id,
                    examen_id,
                    porcentaje_acierto,
                    aciertos,
                    respuestas_incorrectas,
                    fecha,
                ),
            )
            conn.commit()
        flash(
            f"Examen enviado. Porcentaje de acierto: {porcentaje_acierto:.2f}%",
            "success",
        )

    return render_template(
        "examen.html",
        examen=examen,
        asignaturas=get_asignaturas(),
        navbar_data=get_navbar_data(),
        intentos=intentos,
        resultado=resultado,
        porcentaje_acierto=porcentaje_acierto,
    )


@app.route("/examen/<int:examen_id>/resetear_intentos", methods=["POST"])
@login_required
def resetear_intentos(examen_id):
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
    session["dark_mode"] = not session.get("dark_mode", False)
    return redirect(request.referrer or url_for("index"))


def find_free_port(start_port=5000):
    port = start_port
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("0.0.0.0", port))
                return port
            except OSError:
                port += 1


if __name__ == "__main__":
    init_db()  # Inicializa o actualiza la base de datos
    port = find_free_port(5000)
    print(f"Starting server on port {port}...")
    app.run(debug=False, host="0.0.0.0", port=port)
