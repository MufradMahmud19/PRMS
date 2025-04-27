from flask import current_app
from app.models import User
from functools import wraps
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

def init_auth(app):
    pass

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            jwt_required()(f)(*args, **kwargs)
        except Exception as e:
            current_app.logger.error(f"Authentication error: {str(e)}")
            return {'error': 'Authentication required'}, 401
        return f(*args, **kwargs)
    return decorated_function

def create_session(user):
    access_token = create_access_token(identity=str(user.user_id))
    return {
        'access_token': access_token,
        'user': user.to_dict()
    }

def get_current_user():
    try:
        user_id = get_jwt_identity()
        return User.query.get(int(user_id))
    except:
        return None

def logout():
    # JWT tokens are stateless, so we don't need to do anything here
    pass
