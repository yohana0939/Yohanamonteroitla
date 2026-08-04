import os

from flask import Flask, render_template

from .extensions import db, login_manager


def create_app(config_overrides=None):
    app = Flask(__name__, static_folder="../static", template_folder="../templates")
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "yangh-store-dev-secret")

    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "yangh_store.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if config_overrides:
        app.config.update(config_overrides)

    db.init_app(app)
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from .blueprints.main import main_bp
    from .blueprints.auth import auth_bp
    from .blueprints.cart import cart_bp
    from .blueprints.admin import admin_bp
    from .blueprints.despacho import despacho_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(despacho_bp)

    from .blueprints.cart import cart_item_count

    @app.context_processor
    def inject_globals():
        return {"cart_count": cart_item_count()}

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("404.html"), 404

    @app.errorhandler(403)
    def forbidden(_error):
        return render_template("403.html"), 403

    with app.app_context():
        db.create_all()
        _seed_products()
        _seed_usuarios()

    return app


def _seed_products():
    from .data import PRODUCTOS_SEED
    from .models import Product

    if Product.query.first():
        return
    for item in PRODUCTOS_SEED:
        db.session.add(Product(**item))
    db.session.commit()


def _seed_usuarios():
    from .models import User

    if User.query.filter_by(rol="admin").first():
        return

    admin = User(nombre="Administrador", email="admin@yanghstore.com", rol="admin")
    admin.set_password("admin123")

    despachador = User(nombre="Despachador Demo", email="despachador@yanghstore.com", rol="despachador")
    despachador.set_password("despacho123")

    db.session.add_all([admin, despachador])
    db.session.commit()
