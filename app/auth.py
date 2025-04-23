from flask_jwt_extended import create_access_token, jwt_required
from app.models import User
from .app_extensions import jwt

def init_auth(app):
    jwt.init_app(app)
    
    @jwt.user_identity_loader
    def user_identity_lookup(user_id):
        return user_id
    
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return User.query.get(identity)
        
    @jwt.expired_token_loader
    def expired_token_callback(_jwt_header, jwt_data):
        return {"error": "Token has expired"}, 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return {"error": "Invalid token"}, 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return {"error": "Authorization token is missing"}, 401

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(_jwt_header, jwt_data):
        return {"error": "Fresh token required"}, 401

def create_token(user):
    return create_access_token(identity=user.user_id)
