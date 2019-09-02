from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config


# define but do not initialize
db = SQLAlchemy()
async_mode = None


# create factory function
def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])  # load configuration
    config[config_name].init_app(app)

    db.init_app(app=app)

    # register the route blueprint to the app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
