from app.extensions import db
from datetime import datetime
from flask_login import UserMixin
from datetime import datetime
from flask import current_app
from werkzeug.security import check_password_hash
from .helpers import hash_pw

class Blog_Posts(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    date_submitted = db.Column(db.DateTime, default=datetime.utcnow)
    date_to_post = db.Column(db.DateTime, default=datetime.utcnow)
    title = db.Column(db.String(200), nullable=False)
    intro = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    picture_v = db.Column(db.String(200))
    picture_v_source = db.Column(db.String(500))
    picture_h = db.Column(db.String(200))
    picture_h_source = db.Column(db.String(500))
    picture_s = db.Column(db.String(200))
    picture_s_source = db.Column(db.String(500))
    picture_alt = db.Column(db.String(200))
    meta_tag = db.Column(db.String(200))
    title_tag = db.Column(db.String(200))
    admin_approved = db.Column(db.Boolean, default=False)
    # featured is not being used at the moment, in the future can be used to 'feature' a post on a top modal, or similar
    featured = db.Column(db.Boolean, default=False)
    author_id = db.Column(db.Integer, db.ForeignKey('blog_user.id'))
    theme_id = db.Column(db.Integer, db.ForeignKey('blog_theme.id'))
    
    def __repr__(self):
        return f"<Post {self.id}: {self.title}, Theme: {self.theme_id}>"




class Blog_User(UserMixin, db.Model):
    __tablename__ = "blog_user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    email = db.Column(db.String(200), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    about = db.Column(db.String(385), default="")
    # picture's name is saved here, but file saved in static folder
    picture = db.Column(
        db.String(), default="Picture_default.jpg")
    # type can be: admin, super_admin, author, or user
    type = db.Column(db.String(100), nullable=False, default="user")
    blocked = db.Column(db.String(5), default="FALSE")
    admin_notes = db.Column(db.Text)
    posts = db.relationship('Blog_Posts', backref='author')
   

    def __init__(self, **kwargs):
        super(Blog_User, self).__init__(**kwargs)
        if self.type is None or self.type == "user":
            if self.email == current_app.config['SUPERUSER']:
                self.type = "super_user" 

    
    @property
    def password(self):
        raise AttributeError("Password is not a readable attr")
    


    @password.setter
    def password(self, password):
        self.password_hash = hash_pw(password)


    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f"<User: {self.id} {self.name} {self.email}>"


# note that default users will not be added to the stats
# user_total is the total number of users (active or that had their accounts deleted) who created an account 
# user_active_total is the number of users who registered and never deleted their accounts
class Blog_Stats(db.Model):
    __tablename__ = "blog_stats"
    id = db.Column(db.Integer, primary_key=True)
    user_total = db.Column(db.Integer, default=0)
    user_active_total = db.Column(db.Integer, default=0)
    posts_approved = db.Column(db.Integer, default=0)


    def __repr__(self):
        return f"<Comment {self.id}: {self.text}>"
    



# Messages sent through the contact form are saved to the database using this model
# They are, however, not displayed in the admin dashboard, but this can be a further implementation.

class Blog_Contact(db.Model):
    __tablename__ = "blog_contact"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.String(700))


class Blog_Theme(db.Model):
    __tablename__ = "blog_theme"
    id = db.Column(db.Integer, primary_key=True)
    theme = db.Column(db.String(30), nullable=False)
    picture = db.Column(db.String(700), nullable=False)
    picture_source = db.Column(db.String(700))
    posts = db.relationship('Blog_Posts', backref='theme_group')

    def __repr__(self):
        return f"<Theme: {self.id} {self.theme}>"
