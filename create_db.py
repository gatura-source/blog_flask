from app.models import (Blog_Contact, Blog_Posts, Blog_Stats, Blog_Theme, 
                        Blog_User, Role)
from app.extensions import db
from app.dummie_data import authors, posts, themes
from app.helpers import stat_helper
from faker import Faker

fake = Faker()

ADMIN_NAME = "Super Admin"
ADMIN_EMAIL = "super@admin"
ADMIN_PW = "admin123"
ADMIN_PICTURE = "Picture_default.jpg"
DEFAULT_AUTHOR_NAME = "The Travel Blog Team"
DEFAULT_AUTHOR_EMAIL = "travel@team"
DEFAULT_AUTHOR_PW = "author123"
DEFAULT_AUTHOR_ABOUT = authors.authors_about
DEFAULT_AUTHOR_PICTURE = "Picture_default_author.jpg"
DEFAULT_USER_NAME = "[Deleted]"
DEFAULT_USER_EMAIL = "deleted@users"
DEFAULT_USER_PW = "user123"
DEFAULT_USER_ABOUT = "This user's account has been deleted"
DEFAULT_USER_PICTURE = "Picture_default.jpg"


def create_admin_acct():
    # Check if a super_admin exists in the database, if not, add it as well as the default author and default user:
    # Note that these three users will not count towards the number of users using the blog (in the blog stats)
    super_admin_exists = Blog_User.query.get(1)
    if not super_admin_exists:
        the_super_admin = Blog_User(
            name=ADMIN_NAME,
            email=ADMIN_EMAIL,
            password=(ADMIN_PW),
            picture=ADMIN_PICTURE
            )
        the_super_admin.role = Role.query.filter_by(name="ADMIN").first()
        the_default_author = Blog_User(
            name=DEFAULT_AUTHOR_NAME,
            email=DEFAULT_AUTHOR_EMAIL,
            password=(DEFAULT_AUTHOR_PW),
            about=DEFAULT_AUTHOR_ABOUT,
            picture=DEFAULT_AUTHOR_PICTURE
            )
        the_default_author.role = Role.query.filter_by(name="AUTHOR").first()

        the_default_user = Blog_User(
            name=DEFAULT_USER_NAME,
            email=DEFAULT_USER_EMAIL,
            password=(DEFAULT_USER_PW),
            about=DEFAULT_USER_ABOUT,
            picture=DEFAULT_USER_PICTURE
            )
        the_default_user.role = Role.query.filter_by(name="USER").first()
        db.session.add(the_super_admin)
        db.session.add(the_default_author)
        db.session.add(the_default_user)
        db.session.commit()


def create_stats():
    # Check if stats table exists, if not, then add it:
    stats_exists = Blog_Stats.query.get(1)
    if not stats_exists:
        the_stats_table = Blog_Stats()
        db.session.add(the_stats_table)
        db.session.commit()


def create_themes():
    # Check if themes exist in the database, if not, add themes:
    dummies_exists = Blog_Theme.query.get(1)
    if not dummies_exists:
        theme1 = Blog_Theme(
            theme=themes.themes_data[0]["theme"], picture=themes.themes_data[0]["picture"], picture_source=themes.themes_data[0]["picture_source"])
        theme2 = Blog_Theme(
            theme=themes.themes_data[1]["theme"], picture=themes.themes_data[1]["picture"], picture_source=themes.themes_data[1]["picture_source"])
        theme3 = Blog_Theme(
            theme=themes.themes_data[2]["theme"], picture=themes.themes_data[2]["picture"], picture_source=themes.themes_data[2]["picture_source"])
        theme4 = Blog_Theme(
            theme=themes.themes_data[3]["theme"], picture=themes.themes_data[3]["picture"], picture_source=themes.themes_data[3]["picture_source"])

        db.session.add(theme1)
        db.session.add(theme2)
        db.session.add(theme3)
        db.session.add(theme4)
        db.session.commit()


USER_ABOUT = authors.authors_about


def create_dummie_accts():
    # Check if dummies exists in the database, if not, add dummie accounts:
    dummies_exists = Blog_User.query.get(4)
    if not dummies_exists:
        for i in range(10):
            user = Blog_User()
            user.name = fake.name()
            user.email = fake.email()
            user.blocked = False
            user.password = DEFAULT_USER_PW
            user.role = Role.query.filter_by(name="USER").first()
            user.about = fake.paragraph()
            user.picture = authors.authors_data[2]["picture"]
            db.session.add(user)
        db.session.commit()
        stat_helper().user_stats()
        print("Dummy Users Created")


POST_INTRO = posts.post_intro
POST_BODY = posts.post_body


def create_posts():
    posts_exist = Blog_Posts.query.get(1)
    if not posts_exist:
        for i in range(12):
            post = Blog_Posts()
            post.title = fake.text()
            post.title_tag = fake.text()
            post.admin_approved = True
            post.author_id = 0
            post.body = fake.paragraph()
            post.intro = fake.text()
            post.picture_alt = fake.text()
            post.picture_source = posts.post_data[3]["picture_h_source"]

            db.session.add(post)

            db.session.commit()

    stat_helper().post_stats()
    print("Posts created")


def create_contact_db():
    contacts_exist = Blog_Contact.query.get(1)
    if not contacts_exist:
        new_contact = Blog_Contact(
            name="test", email="test", message="test")
        db.session.add(new_contact)
        db.session.commit()
