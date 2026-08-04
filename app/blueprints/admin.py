from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user

from ..constants import CATEGORIAS_PRODUCTO, ESTADOS_PEDIDO, IMAGENES_PRODUCTO, ROLES
from ..decorators import roles_required
from ..extensions import db
from ..models import Order, Product, User
from ..utils import slugify

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def _slug_unico(titulo, producto_actual=None):
    base = slugify(titulo)
    slug = base
    contador = 1
    while True:
        query = Product.query.filter_by(slug=slug)
        if producto_actual:
            query = query.filter(Product.id != producto_actual.id)
        if not query.first():
            return slug
        contador += 1
        slug = f"{base}-{contador}"


def _validar_producto_form(form):
    if not form.get("titulo", "").strip():
        return "El título es obligatorio."
    if not form.get("categoria", "").strip():
        return "La categoría es obligatoria."
    if not form.get("detalle", "").strip():
        return "La descripción es obligatoria."
    try:
        if float(form.get("precio", "")) <= 0:
            return "El precio debe ser mayor a 0."
    except ValueError:
        return "El precio no es válido."
    try:
        if int(form.get("stock", "")) < 0:
            return "El stock no puede ser negativo."
    except ValueError:
        return "El stock no es válido."
    return None


def _valores_iniciales(producto):
    if not producto:
        return {
            "titulo": "", "precio": "", "stock": 0,
            "categoria": CATEGORIAS_PRODUCTO[0], "imagen": IMAGENES_PRODUCTO[0], "detalle": "",
        }
    return {
        "titulo": producto.titulo, "precio": producto.precio, "stock": producto.stock,
        "categoria": producto.categoria, "imagen": producto.imagen, "detalle": producto.detalle,
    }


@admin_bp.route("/")
@roles_required("admin")
def dashboard():
    return render_template(
        "admin/dashboard.html",
        total_productos=Product.query.count(),
        total_pedidos=Order.query.count(),
        total_usuarios=User.query.count(),
        pedidos_pendientes=Order.query.filter_by(estado="Pendiente").count(),
        ultimos_pedidos=Order.query.order_by(Order.fecha.desc()).limit(6).all(),
        bajo_stock=Product.query.order_by(Product.stock).limit(5).all(),
    )


@admin_bp.route("/productos")
@roles_required("admin")
def productos():
    productos = Product.query.order_by(Product.id).all()
    return render_template("admin/productos.html", productos=productos)


@admin_bp.route("/productos/nuevo", methods=["GET", "POST"])
@roles_required("admin")
def producto_nuevo():
    if request.method == "POST":
        error = _validar_producto_form(request.form)
        if error:
            flash(error, "danger")
            return render_template(
                "admin/producto_form.html", producto=None, valores=request.form,
                categorias=CATEGORIAS_PRODUCTO, imagenes=IMAGENES_PRODUCTO,
            )

        titulo = request.form["titulo"].strip()
        producto = Product(
            titulo=titulo,
            slug=_slug_unico(titulo),
            precio=float(request.form["precio"]),
            detalle=request.form["detalle"].strip(),
            categoria=request.form["categoria"].strip(),
            imagen=request.form["imagen"],
            stock=int(request.form["stock"]),
        )
        db.session.add(producto)
        db.session.commit()
        flash(f"Producto '{producto.titulo}' creado.", "success")
        return redirect(url_for("admin.productos"))

    return render_template(
        "admin/producto_form.html", producto=None, valores=_valores_iniciales(None),
        categorias=CATEGORIAS_PRODUCTO, imagenes=IMAGENES_PRODUCTO,
    )


@admin_bp.route("/productos/<int:producto_id>/editar", methods=["GET", "POST"])
@roles_required("admin")
def producto_editar(producto_id):
    producto = Product.query.get_or_404(producto_id)

    if request.method == "POST":
        error = _validar_producto_form(request.form)
        if error:
            flash(error, "danger")
            return render_template(
                "admin/producto_form.html", producto=producto, valores=request.form,
                categorias=CATEGORIAS_PRODUCTO, imagenes=IMAGENES_PRODUCTO,
            )

        producto.titulo = request.form["titulo"].strip()
        producto.precio = float(request.form["precio"])
        producto.stock = int(request.form["stock"])
        producto.categoria = request.form["categoria"].strip()
        producto.detalle = request.form["detalle"].strip()
        producto.imagen = request.form["imagen"]
        db.session.commit()
        flash(f"Producto '{producto.titulo}' actualizado.", "success")
        return redirect(url_for("admin.productos"))

    return render_template(
        "admin/producto_form.html", producto=producto, valores=_valores_iniciales(producto),
        categorias=CATEGORIAS_PRODUCTO, imagenes=IMAGENES_PRODUCTO,
    )


@admin_bp.route("/productos/<int:producto_id>/eliminar", methods=["POST"])
@roles_required("admin")
def producto_eliminar(producto_id):
    producto = Product.query.get_or_404(producto_id)
    nombre = producto.titulo
    db.session.delete(producto)
    db.session.commit()
    flash(f"Producto '{nombre}' eliminado.", "info")
    return redirect(url_for("admin.productos"))


@admin_bp.route("/pedidos")
@roles_required("admin")
def pedidos():
    estado_filtro = request.args.get("estado", "").strip()
    query = Order.query
    if estado_filtro:
        query = query.filter_by(estado=estado_filtro)
    pedidos = query.order_by(Order.fecha.desc()).all()
    return render_template(
        "admin/pedidos.html", pedidos=pedidos, estados=ESTADOS_PEDIDO, estado_filtro=estado_filtro
    )


@admin_bp.route("/pedidos/<int:orden_id>", methods=["GET", "POST"])
@roles_required("admin")
def pedido_detalle(orden_id):
    orden = Order.query.get_or_404(orden_id)
    despachadores = User.query.filter_by(rol="despachador").order_by(User.nombre).all()

    if request.method == "POST":
        nuevo_estado = request.form.get("estado")
        if nuevo_estado in ESTADOS_PEDIDO:
            orden.estado = nuevo_estado

        despachador_id = request.form.get("despachador_id")
        orden.despachador_id = int(despachador_id) if despachador_id else None

        db.session.commit()
        flash(f"Pedido #{orden.id} actualizado.", "success")
        return redirect(url_for("admin.pedido_detalle", orden_id=orden.id))

    return render_template(
        "admin/pedido_detalle.html", orden=orden, despachadores=despachadores, estados=ESTADOS_PEDIDO
    )


@admin_bp.route("/usuarios")
@roles_required("admin")
def usuarios():
    usuarios = User.query.order_by(User.id).all()
    return render_template("admin/usuarios.html", usuarios=usuarios, roles=ROLES)


@admin_bp.route("/usuarios/<int:user_id>/rol", methods=["POST"])
@roles_required("admin")
def usuario_rol(user_id):
    if user_id == current_user.id:
        flash("No puedes cambiar tu propio rol.", "warning")
        return redirect(url_for("admin.usuarios"))

    usuario = User.query.get_or_404(user_id)
    nuevo_rol = request.form.get("rol")
    if nuevo_rol in ROLES:
        usuario.rol = nuevo_rol
        db.session.commit()
        flash(f"Rol de {usuario.nombre} actualizado a '{nuevo_rol}'.", "success")
    return redirect(url_for("admin.usuarios"))
