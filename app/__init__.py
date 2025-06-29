from flask import Flask

def create_app():
    app = Flask(__name__)

    from .routes import main  # assuming you have app/routes.py
    app.register_blueprint(main)

    return app