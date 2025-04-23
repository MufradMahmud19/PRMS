import os
from flask import Flask
from .app_extensions import db, jwt, swagger_ui, cache
from .app_config import Config
from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.json'

swagger_ui = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "Hospital API"}
)

def create_app(config_name=None):
    app = Flask(__name__)
    
    if config_name == 'testing':
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        app.config['CACHE_TYPE'] = 'simple'  # Use simple cache for testing
        app.config['CACHE_DEFAULT_TIMEOUT'] = 2  # 2 seconds timeout for testing
    else:
        app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)

    # Set up authentication
    from .auth import init_auth
    init_auth(app)

    # Initialize cache
    if config_name == 'testing':
        cache.init_app(app)  # Simple cache for testing
    else:
        cache.init_app(app, config={
            'CACHE_TYPE': 'redis',
            'CACHE_REDIS_HOST': app.config['REDIS_HOST'],
            'CACHE_REDIS_PORT': app.config['REDIS_PORT'],
            'CACHE_REDIS_PASSWORD': app.config['REDIS_PASSWORD'],
            'CACHE_REDIS_DB': app.config['REDIS_DB'],
            'CACHE_DEFAULT_TIMEOUT': app.config['CACHE_DEFAULT_TIMEOUT']
        })

    # Setup DB file
    initialize_database(app)

    # Register blueprints
    app.register_blueprint(swagger_ui)
    from .routes import bp
    app.register_blueprint(bp)

    # Register error handlers
    from .errors import init_error_handlers
    init_error_handlers(app)

    return app

def initialize_database(app):
    """Ensure DB folder exists and initialize."""
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    print(f"📍 DB URI: {db_uri}")

    if db_uri.startswith("sqlite:///"):
        db_file = db_uri.replace("sqlite:///", "")
        db_dir = os.path.dirname(db_file)

        print(f"📂 Ensuring directory exists: {db_dir}")
        try:
            os.makedirs(db_dir, exist_ok=True)
        except Exception as e:
            print(f"❌ Could not create DB directory: {e}")
            return

        print(f"🧪 Checking write permissions...")
        if not os.access(db_dir, os.W_OK):
            print(f"❌ No write permissions to: {db_dir}")
            return

    else:
        print("⚠️ Not using SQLite — skipping dir creation.")

    try:
        with app.app_context():
            db.create_all()
            print(f"✅ Database initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")