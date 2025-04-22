import os
from dotenv import load_dotenv  # type: ignore # For environment variables
from datetime import timedelta

# Load .env file if exists
load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instances/hospital.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security (for password hashing)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    
    # API Settings
    JSON_SORT_KEYS = False  # Maintain JSON key order for HATEOAS

    # JWT Settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET') or 'super-secret-hospital-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    # Swagger
    SWAGGER = {
        'title': 'Hospital API',
        'uiversion': 3,
        'specs_route': '/api/docs/'
    }
