from functools import wraps

from flask import abort
from flask_login import current_user, login_required


def roles_required(*roles):
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def wrapped_view(*args, **kwargs):
            if current_user.rol not in roles:
                abort(403)
            return view_func(*args, **kwargs)
        return wrapped_view
    return decorator
