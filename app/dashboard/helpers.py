from flask import current_app
import os
from app.models import Role
from functools import wraps
from flask import abort
from flask_login import current_user


def admin_required():
    def decorated(f):
        @wraps(f)
        def decorated_func(*args, **kwargs):
            if not current_user.role or not current_user.role == Role.query.filter_by(name="ADMIN").first():
                current_app.logger.warning(f"ACCESS DENIED current_user ROLE: {(current_user.role)}: {current_user.email} not superuser")
                abort(403)
            return f(*args, **kwargs)
        return decorated_func
    return decorated


def author_required():
    def decorated(f):
        @wraps(f)
        def decorated_func(*args, **kwargs):
            if not current_user.role or not current_user.role == Role.query.filter_by(name="AUTHOR").first():
                current_app.logger.warning(f" ACCESS DENIED current_user ROLE: {(current_user.role)}: {current_user.email} not author")
                abort(403)
            return f(*args, **kwargs)
        return decorated_func
    return decorated