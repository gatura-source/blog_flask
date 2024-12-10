from app.extensions import db
from sqlalchemy import desc
from flask import current_app

# Functions that take the picture's name and output the path to the source file
def pic_src_post(picture_name):
    return f"../static/Pictures_Posts/{picture_name}"

def pic_src_theme(picture_name):
    return f"../static/Pictures_Themes/{picture_name}"

def pic_src_user(picture_name):
    return f"../static/Pictures_Users/{picture_name}"

# Functions that update the statistics (Stats)


# note that default users will not be added to the stats
def update_stats_users_total(Model):
    """
    Counts number of users who created an account. Does not take into acount users who deleted their accounts.
    This function updates the blog statistics database.
    """
    try:
        stats = Model.query.get_or_404(1)
        modify_stats = int(stats.user_total) + 1
        stats.user_total = modify_stats
        db.session.commit()
    except Exception:
         current_app.logger.error("*update USER TOTAL* Object passed is not an SQL MODEL")
    
# note that default users will not be added to the stats
def update_stats_users_active(Model, num):
    """
    Takes -1 or 1 as arguments. 1 when a user creates an account, -1 when a user deletes an account.
    This function updates the blog statistics database.
    """
    try:
        if num == -1 or num == 1:
            stats = Model.query.get_or_404(1)
            if num == 1:
                modify_stats = int(stats.user_active_total) + 1
                stats.user_active_total = modify_stats
            else:
                modify_stats = int(stats.user_active_total) - 1
                stats.user_active_total = modify_stats
            db.session.commit()
        else:
            return print("Invalid arguments given to def update_stats_users_active function.")
    except Exception:
         current_app.logger.error("*update STATS_user* Object passed is not an SQL MODEL")




    
# takes -1 or 1 as arguments: whether post is approved (1) or disapproved (-1). If a post is approved, then deleted = -1. If a post is deleted but was never approved, do not use this function.
def update_approved_post_stats(Model, num):
    """
    Takes -1 or 1 as arguments. Only to be used on approved posts. -1 if a post is disapproved, 1 when a post is approved.
    If a post was approved, but it then deleted, -1.
    This function updates the blog statistics database.
    """
    try:
        if num == -1 or num == 1:
            stats = Model.query.get_or_404(1)
            if num == 1:
                modify_stats = int(stats.posts_approved) + 1
                stats.posts_approved = modify_stats
            else:
                modify_stats = int(stats.posts_approved) - 1
                stats.posts_approved = modify_stats
            db.session.commit()
        else:
            return print("Invalid arguments given to update_approved_post_stats function.")
    except Exception:
         current_app.logger.error("*Approve POST* Object passed is not an SQL MODEL")



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
        
