from flask_sqlalchemy import SQLAlchemy # type: ignore
from flask_jwt_extended import JWTManager # type: ignore
from flask_swagger_ui import get_swaggerui_blueprint # type: ignore
from flask_caching import Cache # type: ignore

db = SQLAlchemy()
jwt = JWTManager()
cache = Cache()

# Swagger UI
SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/static/swagger.json'  # Our API url (can of course be a local resource)

swagger_ui = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Hospital API",
        'swagger_ui_bundle_js': '//unpkg.com/swagger-ui-dist@3/swagger-ui-bundle.js',
        'swagger_ui_standalone_preset_js': '//unpkg.com/swagger-ui-dist@3/swagger-ui-standalone-preset.js',
        'swagger_ui_css': '//unpkg.com/swagger-ui-dist@3/swagger-ui.css',
        'jquery_js': '//unpkg.com/jquery@2.2.4/dist/jquery.min.js',
        'validatorUrl': None,  # Disable validator
        'displayRequestDuration': True,
        'docExpansion': 'list',
        'defaultModelsExpandDepth': 3,
        'defaultModelExpandDepth': 3,
        'showExtensions': True,
        'showCommonExtensions': True,
        'supportedSubmitMethods': ['get', 'post', 'put', 'delete', 'patch'],
        'persistAuthorization': True,
        'oauth2RedirectUrl': 'http://127.0.0.1:5001/api/docs/oauth2-redirect',
        'deepLinking': True,
        'filter': True,
        'syntaxHighlight.theme': 'monokai',
        'tryItOutEnabled': True
    }
)
