from flask import Flask
from .extensions import db, migrate, login_manager, ckeditor
from app.config import Config
import os
import logging
from logging.handlers import RotatingFileHandler
from .models import Blog_User, Blog_Posts, Blog_Contact, Blog_Stats, Blog_Theme, Role


def register_shell_context(app):
    """Register shell contx objects
    Keyword arguments:
    app -- app instance
    Return: None
    """
    def shell_context():
        return {"db": db,
                "User": Blog_User,
                "Post": Blog_Posts,
                "Contact": Blog_Contact,
                "Stat": Blog_Stats,
                "Theme": Blog_Theme,
                "Role":Role,}
    app.shell_context_processor(shell_context)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class) 
    db.init_app(app)
    migrate.init_app(app=app, db=db)
    ckeditor.init_app(app)
    login_manager.init_app(app)

    from app.account.routes import account
    from app.dashboard.routes import dashboard
    from app.website.routes import website
    from app.error_handlers.routes import error_handler
    from config import Config
    from flask import current_app

    from .models import Blog_User, Blog_Contact, Blog_Stats, Blog_Posts, Blog_Theme

    app.register_blueprint(account)
    app.register_blueprint(dashboard)
    app.register_blueprint(website)
    app.register_blueprint(error_handler)

    @app.route('/test/')
    def test_page():
        return '<h1> Testing the App </h1>'

    ABS_PATH = os.path.dirname(__file__)
    REL_PATH = "static"

    STATIC_PATH = repr(str(app.config["STATIC_FOLDER"]))
    
    @app.route("/../static/<filename>")
    def static_path():
        pass

    register_shell_context(app)

    handler = RotatingFileHandler('app.log', maxBytes=1000000, backupCount=3)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Add the handler to the root logger
    logging.getLogger().addHandler(handler)
    return app
