import os
from dotenv import load_dotenv  # type: ignore # For environment variables
from datetime import timedelta

# Load .env file if exists
load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'hospital.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security (for password hashing)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    
    # API Settings
    JSON_SORT_KEYS = False  # Maintain JSON key order for HATEOAS

    # JWT Settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET') or 'super-secret-hospital-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    JWT_ERROR_MESSAGE_KEY = 'error'
    
    # Redis Configuration
    REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
    REDIS_DB = int(os.environ.get('REDIS_DB', 0))
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', None)
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', 300))  # 5 minutes
    
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
    JWT_SECRET_KEY = 'test-secret-key'
