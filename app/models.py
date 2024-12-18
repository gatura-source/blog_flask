from app.extensions import db
from datetime import datetime
from flask_login import UserMixin
from datetime import datetime, date
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib

Column = db.Column
relationship = db.Relationship
class Permissions:
    """Permissions for church management system."""
    CREATE_USER = 1 << 12  # 4096
    EDIT_USER = 1 << 13  # 8192
    DELETE_USER = 1 << 14  # 16384
    CREATE_BLOG = 1 << 17  # 131072
    EDIT_BLOG = 1 << 18  # 262144
    DELETE_BLOG = 1 << 19  # 524288
    MOD_BLOG = 1 << 20  # 1048576


class Role(db.Model):
    __tablename__ = 'role'
    id = Column(db.Integer, primary_key=True)
    name = Column(db.String(32), nullable=False)
    permissions = Column(db.Integer, default=0)
    users = relationship('Blog_User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs) -> None:
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    @staticmethod
    def create_roles():
        roles = {
            'ADMIN': [getattr(Permissions, x) for x in dir(Permissions)[:7]],
            'AUTHOR': [
                Permissions.CREATE_BLOG, Permissions.EDIT_BLOG,
                Permissions.DELETE_BLOG, Permissions.MOD_BLOG
            ],
            'USER': [0]
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
                role.reset_permissions()
                for perm in roles[r]:
                    role.add_permission(perm)
                db.session.add(role)
            db.session.commit()
            print("[INFO] ROLES ADDED!!")

    def add_permission(self, perm):
        """adds permissions to role
        Keyword arguments:
        perm  -- permissions to add
        Return: None
        """
        try:
            if not self.has_permission(perm):
                self.permissions += perm
                return True
            return False
        except Exception:
            return False
            # abort(500)

    def remove_permission(self, perm):
        """remove permissions
        Keyword arguments:
        perm -- permissions to remove
        Return: return_descr
        """
        try:
            if self.has_permission(perm):
                self.permissions -= perm
                return True
            return False
        except Exception:
            return False

    def has_permission(self, perm: int) -> bool:
        """Check if user has a perm
        Keyword arguments:
        perm  -- permissions to check
        Return: bool
        """
        return self.permissions & perm == perm

    def reset_permissions(self):
        """sets permissions to 0
        Keyword arguments:
        argument -- description
        Return: return_description
        """
        self.permissions = 0

    def __repr__(self) -> str:
        return f'<Role {self.name}>'

class Blog_Posts(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    date_submitted = db.Column(db.DateTime, default=datetime.utcnow)
    date_to_post = db.Column(db.DateTime, default=datetime.utcnow)
    title = db.Column(db.String(200), nullable=False)
    intro = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    picture_source = db.Column(db.String(500))
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
    role_id = Column(db.Integer, db.ForeignKey('role.id'))
    blocked = db.Column(db.Boolean, default=False)
    admin_notes = db.Column(db.Text)
    posts = db.relationship('Blog_Posts', backref='author')
   

    def __init__(self, **kwargs):
        super(Blog_User, self).__init__(**kwargs)
        if self.role is None or self.role == Role.query.filter_by(name="USER").first():
            if self.email == current_app.config['SUPER_USER']:
                self.type = "super_user" 

    
    @property
    def password(self):
        raise AttributeError("Password is not a readable attr")
    


    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)


    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def gravatar_hash(self):
                """
                Creates gravatar from a third party
                """
                return hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()
                
    def gravatar(self, size=100, default = 'identicon', rating='g'):
            """
            Sets user gravatar
            """
            url = "https://secure.gravatar.com/avatar"
            hash = self.gravatar_hash()
            return f"{url}/{hash}?&s={size}&d={default}&r={rating}"
    
    def __repr__(self):
        return f"<User: {self.id} {self.name} {self.email}>"


# note that default users will not be added to the stats
# user_total is the total number of users (active or that had their accounts deleted) who created an account 
# user_active_total is the number of users who registered and never deleted their accounts
class Blog_Stats(db.Model):
    __tablename__ = "blog_stats"
    id = db.Column(db.Integer, primary_key=True)
    user_total = db.Column(db.Integer, default=0)
    user_blocked = db.Column(db.Integer, default=0)
    user_active_total = db.Column(db.Integer, default=0)
    posts_approved = db.Column(db.Integer, default=0)
    posts_pending_approval = db.Column(db.Integer, default=0)
    posts_total = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.Date, default=date.today())


    def __init__(self, **kwargs):
        super(Blog_Stats, self).__init__(**kwargs)
        self.timestamp = date.today()

    
    def user_stats(self):
        active_users = len(
            Blog_User.query.filter(
                Blog_User.is_authenticated == True,
                Blog_User.blocked == False
            ).all()
        )
        blocked_users = len(
            Blog_User.query.filter(
                Blog_User.blocked == True
            ).all()
        )
        total_users = len(
            Blog_User.query.all()
        )
        self.user_total = total_users
        self.user_blocked = blocked_users
        self.user_active_total = active_users
        db.session.commit()


    def post_stats(self):
        active_posts = len(
            Blog_Posts.query.filter(
                Blog_Posts.admin_approved == True
            ).all()
        )
        pending_approval = len(
            Blog_Posts.query.filter(
                Blog_Posts.admin_approved == False
            ).all()
        )
        all_posts = len(Blog_Posts.query.all())
        self.posts_approved = active_posts
        self.posts_pending_approval = pending_approval
        self.posts_total = all_posts
        db.session.commit()

    def __repr__(self):
        return f"<Stat {self.id} >"
    



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
