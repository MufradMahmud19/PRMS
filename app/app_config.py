import os
from dotenv import load_dotenv  # type: ignore # For environment variables
from datetime import timedelta

# Load .env file if exists
load_dotenv()

class Config:
    # Database
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'hospital.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security (for password hashing and sessions)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    
    # API Settings
    JSON_SORT_KEYS = False  # Maintain JSON key order for HATEOAS
    
    # Redis (not used now, using simple cache)
    REDIS_HOST = 'localhost'
    REDIS_PORT = 6379
    REDIS_PASSWORD = None
    REDIS_DB = 0
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
    
    # Cache Settings
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'redis')
    CACHE_REDIS_HOST = REDIS_HOST
    CACHE_REDIS_PORT = REDIS_PORT
    CACHE_REDIS_PASSWORD = REDIS_PASSWORD
    CACHE_REDIS_DB = REDIS_DB
    
    # Swagger
    SWAGGER = {
        'title': 'Hospital API',
        'uiversion': 3,
        'specs_route': '/api/docs/'
    }

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    CACHE_TYPE = 'simple'  # Use simple in-memory cache for testing
    CACHE_DEFAULT_TIMEOUT = 2  # 2 seconds timeout for testing
    WTF_CSRF_ENABLED = False
