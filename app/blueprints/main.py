from flask import Blueprint, render_template, request

from ..models import Product

main_bp = Blueprint("main", __name__)


def _categorias():
    filas = Product.query.with_entities(Product.categoria).distinct().order_by(Product.categoria).all()
    return [fila[0] for fila in filas]


@main_bp.route("/")
def home():
    destacados = Product.query.order_by(Product.id).limit(8).all()
    return render_template("index.html", productos=destacados, categorias=_categorias())


@main_bp.route("/tienda")
def tienda():
    buscar = request.args.get("buscar", "").strip()
    categoria = request.args.get("categoria", "").strip()

    query = Product.query
    if buscar:
        query = query.filter(Product.titulo.ilike(f"%{buscar}%"))
    if categoria:
        query = query.filter_by(categoria=categoria)

    productos = query.order_by(Product.titulo).all()
    return render_template(
        "tienda.html",
        productos=productos,
        categorias=_categorias(),
        buscar=buscar,
        categoria_actual=categoria,
    )


@main_bp.route("/producto/<int:producto_id>")
def producto_detalle(producto_id):
    producto = Product.query.get_or_404(producto_id)
    relacionados = (
        Product.query.filter(Product.categoria == producto.categoria, Product.id != producto.id)
        .limit(4)
        .all()
    )
    return render_template("producto.html", producto=producto, relacionados=relacionados)


@main_bp.route("/acerca")
def acerca():
    return render_template("acerca.html")
