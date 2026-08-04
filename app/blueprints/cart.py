from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required

from ..extensions import db
from ..models import Order, OrderItem, Product

cart_bp = Blueprint("cart", __name__)


def cart_item_count():
    carrito = session.get("carrito", {})
    return sum(carrito.values())


def _cart_lines():
    carrito = session.get("carrito", {})
    lineas = []
    total = 0.0
    cambiado = False

    for producto_id, cantidad in list(carrito.items()):
        producto = Product.query.get(int(producto_id))
        if not producto:
            carrito.pop(producto_id)
            cambiado = True
            continue
        subtotal = producto.precio * cantidad
        total += subtotal
        lineas.append({"producto": producto, "cantidad": cantidad, "subtotal": subtotal})

    if cambiado:
        session["carrito"] = carrito

    return lineas, total


@cart_bp.route("/carrito")
def ver_carrito():
    lineas, total = _cart_lines()
    return render_template("carrito.html", lineas=lineas, total=total)


@cart_bp.route("/carrito/agregar/<int:producto_id>", methods=["POST"])
def agregar(producto_id):
    producto = Product.query.get_or_404(producto_id)
    try:
        cantidad = max(1, int(request.form.get("cantidad", 1)))
    except ValueError:
        cantidad = 1

    carrito = session.get("carrito", {})
    clave = str(producto_id)
    carrito[clave] = carrito.get(clave, 0) + cantidad
    session["carrito"] = carrito

    flash(f"'{producto.titulo}' se agregó al carrito.", "success")
    return redirect(request.referrer or url_for("main.tienda"))


@cart_bp.route("/carrito/actualizar/<int:producto_id>", methods=["POST"])
def actualizar(producto_id):
    try:
        cantidad = int(request.form.get("cantidad", 1))
    except ValueError:
        cantidad = 1

    carrito = session.get("carrito", {})
    clave = str(producto_id)
    if cantidad <= 0:
        carrito.pop(clave, None)
    else:
        carrito[clave] = cantidad
    session["carrito"] = carrito
    return redirect(url_for("cart.ver_carrito"))


@cart_bp.route("/carrito/eliminar/<int:producto_id>", methods=["POST"])
def eliminar(producto_id):
    carrito = session.get("carrito", {})
    carrito.pop(str(producto_id), None)
    session["carrito"] = carrito
    flash("Producto eliminado del carrito.", "info")
    return redirect(url_for("cart.ver_carrito"))


@cart_bp.route("/pago", methods=["GET", "POST"])
@login_required
def pago():
    lineas, total = _cart_lines()
    if not lineas:
        flash("Tu carrito está vacío.", "warning")
        return redirect(url_for("main.tienda"))

    if request.method == "POST":
        for linea in lineas:
            if linea["cantidad"] > linea["producto"].stock:
                flash(f"No hay suficiente stock de '{linea['producto'].titulo}'.", "danger")
                return redirect(url_for("cart.ver_carrito"))

        metodo = request.form.get("metodo_pago", "tarjeta")
        orden = Order(user_id=current_user.id, total=total, metodo_pago=metodo)
        db.session.add(orden)
        db.session.flush()

        for linea in lineas:
            producto = linea["producto"]
            db.session.add(
                OrderItem(
                    order_id=orden.id,
                    product_id=producto.id,
                    titulo=producto.titulo,
                    precio_unitario=producto.precio,
                    cantidad=linea["cantidad"],
                )
            )
            producto.stock = max(0, producto.stock - linea["cantidad"])
        db.session.commit()

        session["carrito"] = {}
        return redirect(url_for("cart.confirmacion", orden_id=orden.id))

    return render_template("pago.html", lineas=lineas, total=total)


@cart_bp.route("/mis-pedidos")
@login_required
def mis_pedidos():
    pedidos = Order.query.filter_by(user_id=current_user.id).order_by(Order.fecha.desc()).all()
    return render_template("mis_pedidos.html", pedidos=pedidos)


@cart_bp.route("/pedido/<int:orden_id>")
@login_required
def confirmacion(orden_id):
    orden = Order.query.get_or_404(orden_id)
    if orden.user_id != current_user.id and current_user.rol != "admin":
        abort(403)
    return render_template("confirmacion.html", orden=orden)
