from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user

from ..constants import ESTADOS_PEDIDO
from ..decorators import roles_required
from ..extensions import db
from ..models import Order

despacho_bp = Blueprint("despacho", __name__, url_prefix="/despacho")


@despacho_bp.route("/")
@roles_required("despachador", "admin")
def panel():
    query = Order.query.filter(Order.despachador_id.isnot(None))
    if current_user.rol == "despachador":
        query = query.filter_by(despachador_id=current_user.id)
    pedidos = query.order_by(Order.fecha.desc()).all()
    return render_template("despacho.html", pedidos=pedidos, estados=ESTADOS_PEDIDO)


@despacho_bp.route("/pedidos/<int:orden_id>/estado", methods=["POST"])
@roles_required("despachador", "admin")
def actualizar_estado(orden_id):
    orden = Order.query.get_or_404(orden_id)
    if current_user.rol == "despachador" and orden.despachador_id != current_user.id:
        abort(403)

    nuevo_estado = request.form.get("estado")
    if nuevo_estado in ESTADOS_PEDIDO:
        orden.estado = nuevo_estado
        db.session.commit()
        flash(f"Pedido #{orden.id} actualizado a '{nuevo_estado}'.", "success")
    return redirect(url_for("despacho.panel"))
