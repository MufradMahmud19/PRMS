from flask_jwt_extended import create_access_token, jwt_required
from app.models import User
from .app_extensions import jwt

def init_auth(app):
    jwt.init_app(app)
    
    @jwt.user_identity_loader
    def user_identity_lookup(user_id):
        print(f"User identity lookup: {user_id}")  # Debug output
        return user_id
    
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        print(f"User lookup callback - JWT data: {jwt_data}")  # Debug output
        print(f"Looking up user with ID: {identity}")  # Debug output
        user = User.query.get(identity)
        if not user:
            print(f"No user found with ID: {identity}")  # Debug output
        return user
        
    @jwt.expired_token_loader
    def expired_token_callback(_jwt_header, jwt_data):
        print(f"Token expired - JWT data: {jwt_data}")  # Debug output
        return {"error": "Token has expired"}, 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        print(f"Invalid token - Error: {error}")  # Debug output
        return {"error": "Invalid token"}, 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        print(f"Missing token - Error: {error}")  # Debug output
        return {"error": "Authorization token is missing"}, 401

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(_jwt_header, jwt_data):
        print(f"Token not fresh - JWT data: {jwt_data}")  # Debug output
        return {"error": "Fresh token required"}, 401

def create_token(user):
    print(f"Creating token for user: {user.user_id}")  # Debug output
    token = create_access_token(identity=user.user_id)
    print(f"Created token: {token}")  # Debug output
    return token
