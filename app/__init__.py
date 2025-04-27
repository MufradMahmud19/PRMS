import os
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from .app_extensions import db, jwt, swagger_ui, cache
from .app_config import Config
from .models import User

def create_app(config_name=None):
    app = Flask(__name__)
    
    # Configure CORS - more permissive for development
    CORS(app, 
         resources={
             r"/*": {  # Allow all routes
                 "origins": ["http://127.0.0.1:5001", "http://localhost:5001"],
                 "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                 "allow_headers": ["Content-Type", "Authorization", "Accept"],
                 "expose_headers": ["Content-Type", "Authorization"],
                 "supports_credentials": True,
                 "max_age": 3600
             }
         })
    
    # Configure static files
    app.static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    app.static_url_path = '/static'
    
    if config_name == 'testing':
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        app.config['CACHE_TYPE'] = 'simple'  # Use simple cache for testing
        app.config['CACHE_DEFAULT_TIMEOUT'] = 2  # 2 seconds timeout for testing
    else:
        app.config.from_object(Config)
        app.config['DEBUG'] = True  # Enable debug mode
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_ECHO'] = True  # Enable SQL query logging
        app.config['CACHE_TYPE'] = 'simple'  # Use simple cache for development
        app.config['CACHE_DEFAULT_TIMEOUT'] = 300  # 5 minutes timeout

    # Configure JWT
    app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Change this to a secure secret key
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600  # 1 hour
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_HEADER_TYPE'] = 'Bearer'
    app.config['JWT_IDENTITY_CLAIM'] = 'sub'

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt.init_app(app)

    # Set up authentication
    from .auth import init_auth
    init_auth(app)

    # Initialize cache
    cache.init_app(app)

    # Setup DB file and create test user
    with app.app_context():
        try:
            db.create_all()
            # Create test user if it doesn't exist
            if not User.query.filter_by(username='dr_smith').first():
                test_user = User(username='dr_smith', role='doctor')
                test_user.set_password('password123')
                db.session.add(test_user)
                db.session.commit()
                print("✅ Test user created successfully!")
            print("✅ Database tables created successfully!")
        except Exception as e:
            print(f"❌ Error creating database tables: {str(e)}")

    # Register blueprints
    app.register_blueprint(swagger_ui)
    from .routes import bp
    app.register_blueprint(bp)

    # Register error handlers
    from .errors import init_error_handlers
    init_error_handlers(app)

    # Add explicit route for swagger.json
    @app.route('/static/swagger.json')
    def serve_swagger():
        return send_from_directory(app.static_folder, 'swagger.json', mimetype='application/json')

    # Root route
    @app.route('/')
    def root():
        return jsonify({
            'message': 'Welcome to Patient Record Management System (PRMS)',
            'version': '1.0.0',
            'description': 'A comprehensive system for managing patient records, visits, and prescriptions',
            'welcome_note': 'Thank you for using our system. Please use the links below to navigate through the application.',
            '_links': {
                'self': {
                    'href': '/',
                    'method': 'GET'
                },
                'api_docs': {
                    'href': '/api/docs',
                    'method': 'GET',
                    'description': 'View API documentation'
                },
                'patients': {
                    'href': '/api/patients',
                    'method': 'GET',
                    'description': 'View all patients'
                },
                'login': {
                    'href': '/api/login',
                    'method': 'POST',
                    'description': 'Login to the system'
                }
            }
        })

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