from app.extensions import db
from flask import current_app
from datetime import date
from app.models import Blog_Stats

# Functions that take the picture's name and output the path to the source file
def pic_src_post(picture_name):
    return f"../static/Pictures_Posts/{picture_name}"

def pic_src_theme(picture_name):
    return f"../static/Pictures_Themes/{picture_name}"

def pic_src_user(picture_name):
    return f"../static/Pictures_Users/{picture_name}"


def stat_helper(d: date = date.today()):
    stat = Blog_Stats.query.filter_by(
        timestamp=d
    ).first()
    if stat is None:
        new_stat = Blog_Stats()
        db.session.add(new_stat)
        return new_stat
    return stat


# Change the authorship of all post
def change_authorship_of_all_post(Model, current_author_id, new_author_id):
    """
    This function changes the authorship of all blog posts associated with an author.
    Arguments: current_author_id and new_author_id
    """
    try: 
        all_posts_from_author = Model.query.filter_by(
            author_id=current_author_id).all()

        for post in all_posts_from_author:
            post.author_id = new_author_id
        db.session.commit()
    except Exception:
        current_app.logger.error("*Authorship CHNG* Object passed is not an SQL MODEL")
        
