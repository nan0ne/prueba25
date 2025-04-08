# from flask import Flask, render_template, request, redirect, url_for
# import sqlite3

# app = Flask(__name__)


# def get_db_connection():
#     conn = sqlite3.connect("database/uned_data.db")
#     conn.row_factory = sqlite3.Row
#     return conn


# @app.route("/")
# def index():
#     conn = get_db_connection()
#     asignaturas = conn.execute("SELECT * FROM asignaturas").fetchall()
#     conn.close()
#     return render_template("index.html", asignaturas=asignaturas)


# @app.route("/asignatura/<int:asignatura_id>")
# def mostrar_asignatura(asignatura_id):
#     conn = get_db_connection()
#     asignatura = conn.execute(
#         "SELECT * FROM asignaturas WHERE id = ?", [asignatura_id]
#     ).fetchone()
#     resumenes_raw = conn.execute(
#         "SELECT * FROM resumenes WHERE asignatura_id = ?", [asignatura_id]
#     ).fetchall()
#     resumenes = [dict(resumen) for resumen in resumenes_raw]

#     examenes_raw = conn.execute(
#         "SELECT * FROM examenes WHERE asignatura_id = ?", [asignatura_id]
#     ).fetchall()
#     examenes = []
#     for examen in examenes_raw:
#         examen_dict = dict(examen)
#         preguntas_raw = conn.execute(
#             "SELECT * FROM preguntas WHERE examen_id = ?", [examen["id"]]
#         ).fetchall()
#         preguntas = []
#         for pregunta in preguntas_raw:
#             pregunta_dict = dict(pregunta)
#             opciones = conn.execute(
#                 "SELECT * FROM opciones WHERE pregunta_id = ?", [pregunta["id"]]
#             ).fetchall()
#             pregunta_dict["opciones"] = [dict(opcion) for opcion in opciones]
#             preguntas.append(pregunta_dict)
#         examen_dict["preguntas"] = preguntas
#         examenes.append(examen_dict)

#     conn.close()
#     return render_template(
#         "asignatura.html", asignatura=asignatura, resumenes=resumenes, examenes=examenes
#     )


# @app.route("/agregar_resumen/<int:asignatura_id>", methods=["GET", "POST"])
# def agregar_resumen(asignatura_id):
#     if request.method == "POST":
#         titulo = request.form["titulo"]
#         contenido = request.form["contenido"]
#         conn = get_db_connection()
#         conn.execute(
#             "INSERT INTO resumenes (asignatura_id, titulo, contenido, es_fijo) VALUES (?, ?, ?, 0)",
#             [asignatura_id, titulo, contenido],
#         )
#         conn.commit()
#         conn.close()
#         return redirect(url_for("mostrar_asignatura", asignatura_id=asignatura_id))

#     return render_template("agregar_resumen.html", asignatura_id=asignatura_id)


# @app.route("/eliminar_resumen/<int:asignatura_id>/<int:resumen_id>", methods=["POST"])
# def eliminar_resumen(asignatura_id, resumen_id):
#     conn = get_db_connection()
#     conn.execute(
#         "DELETE FROM resumenes WHERE id = ? AND asignatura_id = ? AND es_fijo = 0",
#         [resumen_id, asignatura_id],
#     )
#     conn.commit()
#     conn.close()
#     return redirect(url_for("mostrar_asignatura", asignatura_id=asignatura_id))


# if __name__ == "__main__":
#     app.run(debug=True, port=5001)

from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect("database/uned_data.db")
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    conn = get_db_connection()
    asignaturas = conn.execute("SELECT * FROM asignaturas").fetchall()
    conn.close()
    return render_template("index.html", asignaturas=asignaturas)


@app.route("/asignatura/<int:asignatura_id>")
def mostrar_asignatura(asignatura_id):
    conn = get_db_connection()
    asignatura = conn.execute(
        "SELECT * FROM asignaturas WHERE id = ?", [asignatura_id]
    ).fetchone()
    temas_raw = conn.execute(
        "SELECT * FROM temas WHERE asignatura_id = ?", [asignatura_id]
    ).fetchall()
    temas = [dict(tema) for tema in temas_raw]

    examenes_raw = conn.execute(
        "SELECT * FROM examenes WHERE asignatura_id = ?", [asignatura_id]
    ).fetchall()
    examenes = []
    for examen in examenes_raw:
        examen_dict = dict(examen)
        preguntas_raw = conn.execute(
            "SELECT * FROM preguntas WHERE examen_id = ?", [examen["id"]]
        ).fetchall()
        preguntas = []
        for pregunta in preguntas_raw:
            pregunta_dict = dict(pregunta)
            opciones = conn.execute(
                "SELECT * FROM opciones WHERE pregunta_id = ?", [pregunta["id"]]
            ).fetchall()
            pregunta_dict["opciones"] = [dict(opcion) for opcion in opciones]
            preguntas.append(pregunta_dict)
        examen_dict["preguntas"] = preguntas
        examenes.append(examen_dict)

    conn.close()
    return render_template(
        "asignatura.html", asignatura=asignatura, temas=temas, examenes=examenes
    )


@app.route("/agregar_tema/<int:asignatura_id>", methods=["GET", "POST"])
def agregar_tema(asignatura_id):
    if request.method == "POST":
        titulo = request.form["titulo"]
        contenido = request.form["contenido"]
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO temas (asignatura_id, titulo, contenido, es_fijo) VALUES (?, ?, ?, 0)",
            [asignatura_id, titulo, contenido],
        )
        conn.commit()
        conn.close()
        return redirect(url_for("mostrar_asignatura", asignatura_id=asignatura_id))

    return render_template("agregar_tema.html", asignatura_id=asignatura_id)


@app.route("/eliminar_tema/<int:asignatura_id>/<int:tema_id>", methods=["POST"])
def eliminar_tema(asignatura_id, tema_id):
    conn = get_db_connection()
    conn.execute(
        "DELETE FROM temas WHERE id = ? AND asignatura_id = ? AND es_fijo = 0",
        [tema_id, asignatura_id],
    )
    conn.commit()
    conn.close()
    return redirect(url_for("mostrar_asignatura", asignatura_id=asignatura_id))


if __name__ == "__main__":
    app.run(debug=True, port=5001)
