from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from ..extensions import db
from ..models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/registro", methods=["GET", "POST"])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirmar = request.form.get("confirmar", "")

        error = None
        if not nombre or not email or not password:
            error = "Completa todos los campos."
        elif password != confirmar:
            error = "Las contraseñas no coinciden."
        elif len(password) < 6:
            error = "La contraseña debe tener al menos 6 caracteres."
        elif User.query.filter_by(email=email).first():
            error = "Ya existe una cuenta con ese correo."

        if error:
            flash(error, "danger")
            return render_template("registro.html", nombre=nombre, email=email)

        usuario = User(nombre=nombre, email=email)
        usuario.set_password(password)
        db.session.add(usuario)
        db.session.commit()
        login_user(usuario)
        flash(f"¡Bienvenido/a, {usuario.nombre}!", "success")
        return redirect(url_for("main.home"))

    return render_template("registro.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        usuario = User.query.filter_by(email=email).first()

        if usuario and usuario.check_password(password):
            login_user(usuario)
            flash(f"¡Hola de nuevo, {usuario.nombre}!", "success")
            siguiente = request.args.get("next")
            return redirect(siguiente or url_for("main.home"))

        flash("Correo o contraseña incorrectos.", "danger")

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for("main.home"))
