from flask import (Blueprint, render_template, request, redirect,
                   flash, url_for, current_app, abort)
from app.extensions import db
from app.models import (Blog_Posts, Blog_User,
                        Blog_Theme, Role)
from app.dashboard.forms import The_Posts
from app.dashboard.helpers import (admin_required, author_required)
from app.helpers import (change_authorship_of_all_post, 
                         stat_helper)
from datetime import datetime
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from . import dashboard


@dashboard.route("/dashboard/manage_users", methods=["GET", "POST"])
@login_required
@admin_required()
def users_table():
    all_blog_users = Blog_User.query.order_by(Blog_User.id)
    return render_template("dashboard/users_table.html",
                           all_blog_users=all_blog_users)


@dashboard.route("/dashboard/manage_users/update/<int:id>",
                 methods=["GET", "POST"])
@login_required
@admin_required()
def user_update(id):
    acct_types = [role.name for role in Role.query.all() ]
    acct_blocked = {"False": False, "True": True}
    user_to_update = Blog_User.query.get_or_404(id)

    if request.method == "POST":
        if Blog_User.query.filter(Blog_User.id != id,
                                  Blog_User.email == request.form.get("email_update")).first():
            flash("Email Invalid.")
            return render_template("dashboard/users_user_update.html",
                                   id=user_to_update.id,
                                   logged_in=current_user.is_authenticated,
                                   user_to_update=user_to_update,
                                   acct_types=acct_types,
                                   acct_blocked=acct_blocked)
        elif Blog_User.query.filter(Blog_User.id != id,
                                    Blog_User.name == request.form.get("username_update")).first():
            flash("This username is already registered with us.")
            return render_template("dashboard/users_user_update.html",
                                   id=user_to_update.id,
                                   logged_in=current_user.is_authenticated,
                                   user_to_update=user_to_update,
                                   acct_types=acct_types,
                                   acct_blocked=acct_blocked)
        else:
            # if the user to being updated is of type author, if type is updated, posts have to pass to default author first.
            if user_to_update.role.name == "AUTHOR":
                if request.form.get("accttype_update") != Role.query.filter_by(name="AUTHOR").first():
                    change_authorship_of_all_post(Blog_User, user_to_update.id, 2)

            user_to_update.name = request.form.get("username_update")
            user_to_update.email = request.form.get("email_update")
            user_to_update.role = Role.query.filter_by(name=(
                request.form.get('accttype_update')
            )).first()
            user_to_update.blocked = acct_blocked.get(request.form.get('acctblocked_update'))
            try:
                db.session.commit()
                flash("User updated successfully!")
                stat_helper().user_stats()
                return redirect(url_for('dashboard.users_table'))
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Error updating user: {user_to_update.id}: {e}")
                flash("Error, try again.")
                return render_template("dashboard/users_user_update.html", id=user_to_update.id, logged_in=current_user.is_authenticated, user_to_update=user_to_update, acct_types=acct_types, acct_blocked=acct_blocked)
    else:
        return render_template("dashboard/users_user_update.html", logged_in=current_user.is_authenticated, user_to_update=user_to_update, acct_types=acct_types, acct_blocked=acct_blocked)


# Deleting user
@dashboard.route("/dashboard/manage_users/delete/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required()
def user_delete(id):
    if int(id) == 1:
        abort(401)
    user_to_delete = Blog_User.query.get_or_404(id)
    if request.method == "POST":
        try:
            # if user is author, transfer the authorship of the posts to the default author
            if user_to_delete.role.name == "AUTHOR":
                change_authorship_of_all_post(Blog_user, user_to_delete.id, 2)

            # delete user
            db.session.delete(user_to_delete)
            db.session.commit()
            flash("User deleted successfully.")
            stat_helper().user_stats()
            return redirect(url_for('dashboard.users_table'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error deleting user {user_to_delete.id}: {e}")
            flash("There was a problem deleting this user.")
            return render_template("dashboard/users_user_delete.html", logged_in=current_user.is_authenticated, user_to_delete=user_to_delete)
    return render_template("dashboard/users_user_delete.html", logged_in=current_user.is_authenticated, user_to_delete=user_to_delete)

# Blocking user
# Blocking a user will not influence the stats of total active users.
# Blocked users will not be able to log in
@dashboard.route("/dashboard/manage_users/block/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required()
def user_block(id):
    if int(id) == 1:
        abort(401)
    user_to_block = Blog_User.query.get_or_404(id)
    if request.method == "POST":
        try:
            user_to_block.blocked = True
            db.session.commit()
            stat_helper().user_stats()
            flash("User blocked successfully.")
            return redirect(url_for('dashboard.users_table'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error blocking user {user_to_block.id}: {e}")
            flash("There was a problem blocking this user.")
            return render_template("dashboard/users_user_block.html", logged_in=current_user.is_authenticated, user_to_block=user_to_block)
    else:
        return render_template("dashboard/users_user_block.html", logged_in=current_user.is_authenticated, user_to_block=user_to_block)


@dashboard.route("/dashboard/manage_users/unblock/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required()
def user_unblock(id):
    if int(id) == 1:
        abort(401)
    user_to_block = Blog_User.query.get_or_404(id)
    if request.method == "POST" and user_to_block.blocked:
        try:
            user_to_block.blocked = False
            db.session.commit()
            stat_helper().user_stats()
            flash("User unblocked successfully.")
            return redirect(url_for('dashboard.users_table'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error unblocking user {user_to_block.id}: {e}")
            flash("There was a problem unblocking this user.")
            return render_template("dashboard/users_user_unblock.html", logged_in=current_user.is_authenticated, user_to_block=user_to_block)
    else:
        return render_template("dashboard/users_user_unblock.html", logged_in=current_user.is_authenticated, user_to_block=user_to_block)
    
# Previewing a user's account information
@dashboard.route("/dashboard/manage_users/preview/<int:id>")
@login_required
@admin_required()
def user_preview(id):
    user_to_preview = Blog_User.query.get_or_404(id)
    return render_template("dashboard/users_user_preview.html", logged_in=current_user.is_authenticated, user_to_preview=user_to_preview)

# ***********************************************************************************************
# POST MANGEMENT

# ADDING NEW BLOG POST -  AUTHORS ONLY
# Only users of type authors can add new posts
@dashboard.route("/dashboard/submit_new_post", methods=["GET", "POST"])
@login_required
@author_required()
def submit_post():
    themes_list = [(u.id, u.theme) for u in db.session.query(Blog_Theme).all()]
    form = The_Posts(obj=themes_list)
    form.theme.choices = themes_list

    if request.method == "POST":
        if form.validate_on_submit():
            post = Blog_Posts()
            post.theme_id = form.theme.data
            post.author_id = current_user.id
            post.body = form.body.data
            post.title = form.title.data
            post.intro = form.intro.data
            post.date_to_post = form.date.data
            post.title_tag = form.title_tag.data
            post.meta_tag = form.meta_tag.data
            post.picture_source= form.picture_source.data
            post.picture_alt = form.picture_alt.data
            try:
                db.session.add(post)
                db.session.commit()
                flash("Post add Success")
                stat_helper().post_stats()
                return redirect(url_for('account.dashboard'))

            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Error Saving Post {post} to db: {e}")
                flash("Error saving your blog post, check all fields and try again.")
                return redirect(url_for('account.dashboard'))

    return render_template("dashboard/posts_submit_new.html", form=form)


@dashboard.route("/dashboard/manage_posts")
@admin_required()
@login_required
def posts_table():
    all_blog_posts_submitted = Blog_Posts.query.order_by(Blog_Posts.id)
    return render_template("dashboard/posts_table.html", 
                           all_blog_posts_submitted=all_blog_posts_submitted)

# Approve posts: only users of type admin can approve posts
# Approved posts are published on the blog
# When a post is approved, this will count towards active posts in the blog statictics.

@dashboard.route("/dashboard/manage_posts/approve_post/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required()
def approve_post(id):
    post_to_approve = Blog_Posts.query.get_or_404(id)
    if request.method == "POST":
        post_to_approve.admin_approved = True
        try:
            db.session.commit()
            flash("This post has been admin approved.")
            stat_helper().post_stats()
            return redirect(url_for('dashboard.posts_table'))
        except:
            flash("There was a problem approving this post.")
            db.session.rollback()
            return render_template("dashboard/posts_approve_post.html", post_to_approve=post_to_approve)
    else:
        return render_template("dashboard/posts_approve_post.html", post_to_approve=post_to_approve)

# Disapprove (disallow) posts: only user accounts of type admin can disapprove a post
# Disapproving a post will unpublish it from the blog
# This action will be reflected in the blog stats of active posts
@dashboard.route("/dashboard/manage_posts/disallow_post/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required()
def disallow_post(id):
    post_to_disallow = Blog_Posts.query.get_or_404(id)
    if request.method == "POST":
        post_to_disallow.admin_approved = False
        try:
            db.session.commit()
            flash("This post is no longer admin approved.")
            stat_helper().post_stats()
            return redirect(url_for('dashboard.posts_table'))
        except:
            flash("There was a problem disallowing this post.")
            db.session.rollback()
            return render_template("dashboard/posts_disallow_post.html", post_to_disallow=post_to_disallow)
    else:
        return render_template("dashboard/posts_disallow_post.html",  post_to_disallow=post_to_disallow)

# POST MANAGEMENT - AUTHORS DASH
# View table with all posts this author has submitted
@dashboard.route("/dashboard/manage_posts_author")
@login_required
@author_required()
def posts_table_author():
    all_blog_posts_submitted = Blog_Posts.query.filter(
        Blog_Posts.author_id == current_user.id).all()
    return render_template("dashboard/posts_table_author.html", logged_in=current_user.is_authenticated, all_blog_posts_submitted=all_blog_posts_submitted)


# POST MANGEMENT -  ADMIN AND AUTHORS
# Previewing a post
@dashboard.route("/dashboard/manage_posts_author/preview_post/<int:id>", endpoint='preview_post_author')
@dashboard.route("/dashboard/manage_posts/preview_post/<int:id>")
@login_required
def preview_post(id):
    post_to_preview = Blog_Posts.query.get_or_404(id)
    if not (current_user.role == Role.query.filter_by(name="ADMIN").first()
            or current_user == post_to_preview.author):
        abort(403)
    return render_template("dashboard/posts_preview_post.html", logged_in=current_user.is_authenticated, post_to_preview=post_to_preview)

# Editing a post - ADMIN AND AUTHORS
#make authors as a list
@dashboard.route("/dashboard/manage_posts_author/edit_post/<int:id>", endpoint='edit_post_author', methods=["GET", "POST"])
@dashboard.route("/dashboard/manage_posts/edit_post/<int:id>", methods=["GET", "POST"])
@login_required
def edit_post(id):
    post_to_edit = Blog_Posts.query.get_or_404(id)
    if not (current_user == post_to_edit.author or 
            current_user.role == Role.query.filter_by(name="ADMIN").first()):
        abort(403)
    themes_list = [(u.id, u.theme) for u in db.session.query(Blog_Theme).all()]
    form = The_Posts(obj=themes_list)
    form.theme.choices = themes_list
    if request.method == "POST" :
        if form.validate_on_submit():
            post_to_edit.theme_id = form.theme.data
            post_to_edit.date_to_post = form.date.data
            post_to_edit.title = form.title.data
            post_to_edit.intro = form.intro.data
            post_to_edit.body = form.body.data
            post_to_edit.picture_source = form.picture_source.data
            post_to_edit.picture_alt = form.picture_alt.data
            post_to_edit.meta_tag = form.meta_tag.data
            post_to_edit.title_tag = form.title_tag.data
            try:
                db.session.commit()
                if current_user.role.name == "ADMIN":
                    flash("Post Edit success")
                    return redirect(url_for("dashboard.posts_table"))
                elif current_user.role.name == "AUTHOR":
                    flash("Post Edit Success")
                    return redirect(url_for("dashboard.posts_table_author"))
                else:
                    abort(403)
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"ERROR while editing Post {post_to_edit.id}: {e}")
                flash("Post edit Error")
    form.theme.data = post_to_edit.theme_id
    form.author.data = post_to_edit.author.name
    form.date.data = post_to_edit.date_to_post
    form.title.data = post_to_edit.title
    form.intro.data = post_to_edit.intro
    form.body.data = post_to_edit.body
    form.picture_source.data = post_to_edit.picture_source
    form.picture_alt.data = post_to_edit.picture_alt
    form.meta_tag.data = post_to_edit.meta_tag
    form.title_tag.data = post_to_edit.title_tag
    return render_template('dashboard/posts_edit_post.html', logged_in=current_user.is_authenticated, form=form, post_to_edit=post_to_edit)   
        
    
# Deleting a post 
@dashboard.route("/dashboard/manage_posts_author/delete_post/<int:id>", endpoint='delete_post_author', methods=["GET", "POST"])
@dashboard.route("/dashboard/manage_posts/delete_post/<int:id>", methods=["GET", "POST"])
@login_required
def delete_post(id, methods=['POST']):
    if request.method == 'POST':
        try:
            post_to_delete = Blog_Posts.query.get_or_404(id)
            if not (current_user.role == Role.query.filter_by(name="ADMIN").first()
                    or current_user == post_to_delete.author):
                abort(403)
            db.session.delete(post_to_delete)
            db.session.commit()
            flash("Post delete success")
            stat_helper().post_stats()
            if current_user.role.name == "AUTHOR":
                return redirect(url_for('dashboard.posts_table_author'))
            elif current_user.role.name == "ADMIN":
                return redirect(url_for('dashboard.posts_table'))
            else:
                abort(403)
        except Exception as e:
            db.session.rollback()
            flash("Error Deleting Post")
            current_app.logger.info(f"Error Deleting Post {id}: {e}")
            if current_user.role.name == "AUTHOR":
                return redirect(url_for('dashboard.posts_table_author'))
            elif current_user.role.name == "ADMIN":
                return redirect(url_for('dashboard.posts_table'))
            else:
                abort(403)
    return render_template(
        "dashboard/posts_delete_post.html",
        post_to_delete=Blog_Posts.query.get_or_404(id))
