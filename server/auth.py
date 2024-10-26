from functools import wraps
from flask import session, jsonify

def role_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            if 'user_id' not in session:
                return jsonify(msg="Unauthorized"), 401
            if session.get('role') not in roles:
                return jsonify(msg="Forbidden"), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return {'message': 'Unauthorized'}, 401
        return f(*args, **kwargs)
    return decorated_function