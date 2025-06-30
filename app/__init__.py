from flask import Flask

def create_app():
    app = Flask(__name__)

    from .routes import main, auth
    app.register_blueprint(main)
    app.register_blueprint(auth)

    return app