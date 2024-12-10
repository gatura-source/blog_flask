from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
ckeditor = CKEditor()
login_manager = LoginManager()
migrate = Migrate()
