from flask import Flask
from .table.views import table

def create_app():
    app = Flask(__name__)
    app.register_blueprint(table, url_prefix='/table/')
    return app