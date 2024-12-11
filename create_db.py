from flask import current_app
from app.models import Blog_Contact, Blog_Posts, Blog_Stats, Blog_Theme, Blog_User
from app.extensions import db
# from app.models.text import about_text_author, about_text_user  # dummie strings
from app.dummie_data import authors, posts, themes, comments
# from app.helpers import hash_pw
from app.helpers import pic_src_user, pic_src_post, pic_src_theme, update_approved_post_stats
from datetime import datetime
from faker import Faker

fake = Faker()

# Creating a super_admin, a default author account, and a default user account
# The super_admin is important as this will enable the management of all other users.
# The default author is created for the case of an author having his/her account deleted: the posts
# created by this user will be passed onto the default author's account, to avoid loss of online content.
# The default user is created to avoid the loss of comments when a user's account it deleted: it will 'gain ownership' of deleted comments to prevent mismatch in treads.
# you can re-define the log-in credentials for these users by changing the variables bellow.
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
            name=ADMIN_NAME, email=ADMIN_EMAIL, password=(ADMIN_PW), type="super_admin", picture=ADMIN_PICTURE)
        the_default_author = Blog_User(name=DEFAULT_AUTHOR_NAME, email=DEFAULT_AUTHOR_EMAIL, password=(DEFAULT_AUTHOR_PW),
                                    type="author", about=DEFAULT_AUTHOR_ABOUT, picture=DEFAULT_AUTHOR_PICTURE)
        the_default_user = Blog_User(name=DEFAULT_USER_NAME, email=DEFAULT_USER_EMAIL, password=(DEFAULT_USER_PW),
                                    type="user", about=DEFAULT_USER_ABOUT, picture=DEFAULT_USER_PICTURE)
        db.session.add(the_super_admin)
        db.session.add(the_default_author)
        db.session.add(the_default_user)
        db.session.commit()

# Creating the stats
def create_stats():
    # Check if stats table exists, if not, then add it:
    stats_exists = Blog_Stats.query.get(1)
    if not stats_exists:
        the_stats_table = Blog_Stats()
        db.session.add(the_stats_table)
        db.session.commit()

# Creating the themes
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

# DUMMIE DATA
# Users, posts, comments, likes, and bookmarks were created for the purposes of testing and previewing the application
# These can be deleted. Plese note, however, that if you delete the posts without replacing them with new data, the blog may present a number of issues.
# Likewise, deleting the author's account created in this page without changing the authorship of the posts (or deleting the posts) will leave to issues.
# Dummie users are linked to data such as comments and likes. Deleting the creation of these without edditing or deleting their actions will result in  issues.

# Creating dummie user accounts: to test and use the app as example
# These users can be deleted without impacting the blog's usage
USER_PW = "user123"
USER_ABOUT = authors.authors_about

def create_dummie_accts():
    # Check if dummies exists in the database, if not, add dummie accounts:
    dummies_exists = Blog_User.query.get(4)
    if not dummies_exists:
        random1 = Blog_User(name="Roberta Sanstoms",
                            email="r@r", password=hash_pw(USER_PW), type="admin")
        random2 = Blog_User(name=authors.authors_data[0]["name"], email="e@e", password=hash_pw(USER_PW),
                            type="author", about=USER_ABOUT, picture=authors.authors_data[0]["picture"])
        random3 = Blog_User(name=authors.authors_data[1]["name"], email="j@j", password=hash_pw(USER_PW),
                            type="author", about=USER_ABOUT, picture=authors.authors_data[1]["picture"])
        random4 = Blog_User(name=authors.authors_data[2]["name"], email="m@m", password=hash_pw(USER_PW),
                            type="author", about=USER_ABOUT, picture=authors.authors_data[2]["picture"])
        random5 = Blog_User(name="John Meyers", email="j@m",
                            password=hash_pw(USER_PW), type="user")
        random6 = Blog_User(name="Fabienne123", email="f@f",
                            password=hash_pw(USER_PW), type="user")
        random7 = Blog_User(name="Kokaloka", email="k@k",
                            password=hash_pw(USER_PW), type="user")
        random8 = Blog_User(name="SublimePoster", email="s@p",
                            password=hash_pw(USER_PW), type="user")
        db.session.add(random1)
        db.session.add(random2)
        db.session.add(random3)
        db.session.add(random4)
        db.session.add(random5)
        db.session.add(random6)
        db.session.add(random7)
        db.session.add(random8)
        db.session.commit()
        for i in range(8):
            update_stats_users_total()
            update_stats_users_active(1)


# Creating dummie posts: to test and use the app as example
POST_INTRO = posts.post_intro
POST_BODY = posts.post_body
def create_posts():
    # Check if dummie posts exists in the database, if not, create the posts:
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
            post.picture_h = posts.post_data[3]["picture_h"]
            post.picture_v = posts.post_data[3]["picture_v"]
            post.picture_s = posts.post_data[3]["picture_s"]
            post.picture_h_source = posts.post_data[3]["picture_h_source"]
            post.picture_v_source = posts.post_data[3]["picture_v_source"]
            post.picture_s_source = posts.post_data[3]["picture_h_source"]

            db.session.add(post)

            db.session.commit()

            update_approved_post_stats(Blog_Posts, 1)
        
    print("Posts created")




# Testing the contact model:
def create_contact_db():
    contacts_exist = Blog_Contact.query.get(1)
    if not contacts_exist:
        new_contact = Blog_Contact(
            name="test", email="test", message="test")
        db.session.add(new_contact)
        db.session.commit()

if __name__ == '__main__':
    create_admin_acct()
    create_posts()