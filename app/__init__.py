from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from config import config
from flask_login import LoginManager


# define but do not initialize
db = SQLAlchemy()
async_mode = None
bootstrap = Bootstrap()
moment = Moment()
login_manager = LoginManager()

# set login manager
login_manager.session_protection = 'strong'
login_manager.login_view = 'login.index'


# create factory function
def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])  # load configuration
    config[config_name].init_app(app)

    db.init_app(app=app)
    bootstrap.init_app(app=app)
    moment.init_app(app=app)
    login_manager.init_app(app=app)

    # register the route blueprint to the app
    from .auth import auth as auth_blueprint
    from .main import main as main_blueprint
    from .api01 import api as api_blueprint
    from .login import login as login_blueprint
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(api_blueprint)
    app.register_blueprint(login_blueprint)

    return app
