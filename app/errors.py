from flask import jsonify, request # type: ignore
from werkzeug.exceptions import HTTPException # type: ignore
from .hateoas import Hateoas

def init_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_error(e):
        hateoas = Hateoas(request.host_url)
        response = jsonify({
            "error": e.description,
            "_links": hateoas.error_links(e.code)
        })
        response.status_code = e.code
        return response

    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        hateoas = Hateoas(request.host_url)
        response = jsonify({
            "error": "Internal server error",
            "_links": hateoas.error_links(500)
        })
        response.status_code = 500
        return response
