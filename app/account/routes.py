from flask import (render_template, request, redirect,
                   flash, url_for, current_app, abort)
from app.extensions import db, login_manager
from app.models import (Blog_Posts, Blog_User, Role, Blog_Stats, Blog_Contact)
from app.account.forms import The_Accounts
from app.helpers import (
    change_authorship_of_all_post, stat_helper)
from flask_login import login_user, login_required, current_user, logout_user
from sqlalchemy import desc
from datetime import datetime
from ..dashboard.helpers import admin_required
from . import account


# Pages: login, logout, signup, account
# Routes available for all registered users (all user types) + login
# and signup (available for all registered and non-registered users)

# ***********************************************************************************************
# LOGIN, SIGN UP, LOG OUT
@login_manager.user_loader
def load_user(user_id):
    return Blog_User.query.get(int(user_id))


@account.route("/signup", methods=["GET", "POST"])
def signup():
    # Future improvement tip: check if username is unique
    if request.method == "POST":
        if Blog_User.query.filter_by(email=request.form.get("email")).first():
            # if user already exists:
            flash("This email is already registered with us. Log-in instead!")
            return redirect(url_for("account.login"))

        new_user = Blog_User(
            name=request.form.get("username"),
            email=request.form.get("email"),
            password=(request.form.get("password")),
        )
        new_user.role = Role.query.filter_by(name="USER").first()
        db.session.add(new_user)
        db.session.commit()
        stat_helper().user_stats()

        login_user(new_user)

        return redirect(url_for('account.dashboard'))

    return render_template('account/signup.html',
                           logged_in=current_user.is_authenticated)


@account.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('website.home'))


@account.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        the_user = Blog_User.query.filter_by(email=email).first()
        # wrong email:
        if not (the_user or the_user.verify_password(password)):
            flash("Wrong Password or Email")
            return redirect(url_for("account.login"))
        # user is blocked:
        elif the_user.blocked:
            flash("Your account has been blocked. Please contact us for more"
                  "information")
            return redirect(url_for("account.login"))
        # email exists and password is correct:
        else:
            login_user(the_user)
            return redirect(url_for("account.dashboard"))
    return render_template("account/login.html")


# ***********************************************************************************************
# DASHBOARDs
# displaying user dashboard after log-in according to the account type: user,
# author, or admin
@account.route('/dashboard')
@login_required
def dashboard():
    if current_user.role is None:
        abort(403)
    match current_user.role.name:
        case ("USER"):
            posts = Blog_Posts.query.filter(
                Blog_Posts.admin_approved is True,
                Blog_Posts.date_to_post <= datetime.utcnow()
            ).order_by(desc(Blog_Posts.date_to_post)).limit(3)
            return render_template('account/dashboard_user.html', posts=posts)
        case ("AUTHOR"):
            posts_pending_admin = Blog_Posts.query.filter(
                Blog_Posts.author_id == current_user.id,
                Blog_Posts.admin_approved is False
            ).all()
            return render_template('account/dashboard_author_dash.html',
                                   posts_pending_admin=posts_pending_admin)
        case ("ADMIN"):
            stats = Blog_Stats.query.all()[-1]
            posts_app = Blog_Posts.query.filter(
                Blog_Posts.admin_approved is False
            ).all()
            return render_template('account/dashboard_admin_dash.html',
                                   posts_pending_approval=posts_app,
                                   current_stats=stats)
        case (_):
            abort(403)


@account.route("/dashboard/manage_account")
@login_required
def manage_acct():
    return render_template("account/account_mgmt.html")


@account.route("/dashboard/manage_account/update/<int:id>",
               methods=["GET", "POST"])
@login_required
def update_own_acct_info(id):
    form = The_Accounts()
    user_at_hand = Blog_User.query.get_or_404(id)

    if form.validate_on_submit():
        user_at_hand.name = form.username.data
        user_at_hand.email = form.email.data
        user_at_hand.about = form.about.data

        try:
            db.session.commit()
            flash("Account information updated successfully!")
            return redirect(url_for('account.manage_acct'))
        except Exception as e:
            current_app.logger.error(f"Error updating user {current_user.id}information: {e}")
            flash("Oops, error updating account information, try again.")
            return redirect(url_for('account.manage_acct'))

    # filling out the form with saved post data
    form.username.data = user_at_hand.name
    form.email.data = user_at_hand.email
    form.about.data = user_at_hand.about
    return render_template("account/account_mgmt_update.html",  form=form)


# Delete account
@account.route("/dashboard/manage_account/delete/<int:id>",
               methods=["GET", "POST"])
@login_required
@admin_required()
def delete_own_acct(id):
    if id == 1:
        current_app.logger.warning(f" {current_user.id} Tried deleting admin")
        abort(403)
    user_at_hand = Blog_User.query.get_or_404(id)
    if request.method == "POST":
        try:
            if user_at_hand.role == Role.query.filter_by(name="AUTHOR").first():
                change_authorship_of_all_post(Blog_User, user_at_hand.id, 2)
            # delete user
            db.session.delete(user_at_hand)
            db.session.commit()
            flash("Your account was deleted successfully.")
            stat_helper().user_stats()
            return redirect(url_for("website.home"))
        except Exception as e:
            flash("There was a problem deleting your account.")
            db.session.rollback()
            current_app.logger.info(f"Error deleting user ID: {current_user.id}: {e}")
            return redirect(url_for('account.manage_acct'))
    else:
        return render_template("account/account_mgmt_delete.html",)


@account.route("/dashboard/inbox", methods=["GET"])
@login_required
@admin_required()
def inbox():
    contacts = Blog_Contact.query.all()
    return render_template("account/inbox.html", contacts=contacts)
