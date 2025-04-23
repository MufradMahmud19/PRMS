from flask_sqlalchemy import SQLAlchemy # type: ignore
from flask_jwt_extended import JWTManager # type: ignore
from flask_swagger_ui import get_swaggerui_blueprint # type: ignore
from flask_caching import Cache # type: ignore

db = SQLAlchemy()
jwt = JWTManager()
cache = Cache()

# Swagger UI
swagger_ui = get_swaggerui_blueprint(
    base_url='/api/docs',
    api_url='/static/swagger.json',
    config={'app_name': "Hospital API"}
)
