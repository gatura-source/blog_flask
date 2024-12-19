from flask import Blueprint, render_template, request, jsonify, make_response, current_app
from app.extensions import db
from app.website.contact import send_email
from app.models import (Blog_Theme, Blog_Contact, Blog_Posts, Blog_Stats, Blog_User, Role)
from flask_login import current_user
from datetime import datetime
from sqlalchemy import desc
from . import website

# Blog website pages: Home Page, All posts, About, Contact page
# Routes available for registered and non-registered users alike

@website.route("/")
def home():
    post_themes = Blog_Theme.query.all()
    all_posts = {}
    for theme in post_themes:
        all_posts[theme] = []
    for theme in all_posts.keys():
        for post in Blog_Posts.query.filter(
            Blog_Posts.admin_approved == True,
        ).all():
            if post.theme_id == theme.id:
                all_posts[theme].append(post)
    for theme in post_themes:
        all_posts[theme] = all_posts[theme][:1]
    current_app.logger.info(f"themes: {post_themes}: posts: {all_posts}")
    
    return render_template('website/index.html', themes=post_themes, all_posts=all_posts)

# route to 'All Posts' page or page by chosen theme
@website.route("/all/<int:index>")
def all(index):
    index = int(index)
    all_blog_posts = None
    chosen_theme = ""
    intros = []
    if index != 0:
        chosen_theme = db.session.query(
            Blog_Theme).filter(Blog_Theme.id == index).first().theme
        all_blog_posts = db.session.query(Blog_Posts).filter(Blog_Posts.theme_id == index,
            Blog_Posts.admin_approved == True, Blog_Posts.date_to_post <= datetime.utcnow(),
        ).order_by(desc(Blog_Posts.date_to_post)).limit(25)
    else:
        all_blog_posts = db.session.query(Blog_Posts).filter(
            Blog_Posts.admin_approved == True, Blog_Posts.date_to_post <= datetime.utcnow(),
            ).order_by(desc(Blog_Posts.date_to_post)).limit(25)
    for post in all_blog_posts:
        if len(post.intro) > 300:
            cut_intro_if_too_long = f"{post.intro[:300]}..."
            intros.append(cut_intro_if_too_long)
        else:
            intros.append(post.intro)

    return render_template('website/all_posts.html', all_blog_posts=all_blog_posts, chosen_theme=chosen_theme, intros=intros, logged_in=current_user.is_authenticated)

@website.route("/about/")
def about():
    authors = Blog_User.query.filter(
        Blog_User.blocked == False,
        Blog_User.role == Role.query.filter_by(name="AUTHOR").first()
    ).order_by(
        desc(Blog_User.id)
    ).limit(25)
    return render_template('website/about.html', authors_all=authors)
    
@website.route("/contact/", methods=['POST', 'GET'])
def contact():
    if request.method == "POST":
        contact_name = request.form['contact_name']
        contact_email = request.form['contact_email']
        contact_message = request.form['contact_message']
        new_contact = Blog_Contact(
            name=contact_name, email=contact_email, message=contact_message)
        try:
            # push to database:
            db.session.add(new_contact)
            db.session.commit()
            # send email:
            send_email(contact_name, contact_email, contact_message)
            return render_template('website/contact.html', msg_sent=True)
        except:
            current_app.logger.error("There was an error adding contact message to the database.")
    return render_template('website/contact.html', msg_sent=False)


@website.route("/post/<int:index>", methods=["GET", "POST"])
def blog_post(index):
    # get the post
    blog_post = db.session.query(Blog_Posts).filter(Blog_Posts.id == index,
                                                    Blog_Posts.admin_approved == True, Blog_Posts.date_to_post <= datetime.utcnow(),
                                                    ).order_by(Blog_Posts.date_submitted.desc()).first()
    return render_template('website/post.html', blog_posts=blog_post)
