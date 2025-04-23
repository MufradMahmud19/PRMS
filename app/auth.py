from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from app.models import User

jwt = JWTManager()

def init_auth(app):
    jwt.init_app(app)
    
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        return user.user_id
    
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return User.query.get(identity)

def create_token(user):
    return create_access_token(identity=user)
