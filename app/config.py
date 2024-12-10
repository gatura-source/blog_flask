import os
from dotenv import load_dotenv  # getting .env variables
from datetime import timedelta

load_dotenv()
base_path = os.path.abspath(os.getcwd())

class Config:
    SUPER_USER = os.getenv("SUPERUSER") 
    SECRET_KEY = "myFlaskApp4Fun"  # needed for login with wtforms
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(base_path, os.getenv("DBNAME"))}" 
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEMPLATES_AUTO_RELOAD = True
    ABSOLUTE_PATH = os.path.dirname(__file__)
    RELATIVE_PATH = "static/Pictures_Users"
    BLOG_PICTURES_PATH = "static/Pictures_Posts"
    PROFILE_IMG_FOLDER = os.path.join(ABSOLUTE_PATH, RELATIVE_PATH)
    BLOG_IMG_FOLDER = os.path.join(ABSOLUTE_PATH, BLOG_PICTURES_PATH)
    STATIC_FOLDER = os.path.join(ABSOLUTE_PATH, "static")
    ALLOWED_IMG_EXTENSIONS = ['PNG', 'JPG', 'JPEG']
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

