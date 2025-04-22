from flask import Flask
from .extensions import db, jwt, swagger_ui
from .config import Config
from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = '/api/docs'  # URL for accessing the UI
API_URL = '/static/swagger.json'  # Your API spec file location

swagger_ui = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "Hospital API"}
)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    from .auth import init_auth
    init_auth(app)
    
    # Register blueprints
    app.register_blueprint(swagger_ui)
    
    # Import and register routes
    from .routes import bp
    app.register_blueprint(bp)

    # Registering handlers
    from .errors import init_error_handlers
    init_error_handlers(app)
    
    return app
