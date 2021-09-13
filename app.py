#################################################
# Flask Setup
#################################################
import os
from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    redirect,
    abort,
    session)
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import sqlalchemy
from flask_mail import Mail, Message
from config import mail_username, mail_password
from wtforms import TextAreaField
from wtforms.widgets import TextArea

#################################################
# Flask Setup
#################################################
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@localhost:5432/medicine_without"
# Secret Key for being able to post back to database
app.config["SECRET_KEY"] = "$MedicineWithout2021$"
# SMTP Mail Server - outlook
app.config["MAIL_SERVER"] = "smtp-mail.outlook.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False
app.config["MAIL_USERNAME"] = mail_username
app.config["MAIL_PASSWORD"] = mail_password
# app.config["MAIL_SUPPRESS_SEND"] = False

# Create db object
db = SQLAlchemy(app)
# Create admin page object
admin = Admin(app)
# Create mail object
mail = Mail(app)

#################################################
# Database tables via classes
#################################################
class CKTextAreaWidget(TextArea):
    def __call__(self, field, **kwargs):
        if kwargs.get('class'):
            kwargs['class'] += ' ckeditor'
        else:
            kwargs.setdefault('class', 'ckeditor')
        return super(CKTextAreaWidget, self).__call__(field, **kwargs)

class CKTextAreaField(TextAreaField):
    widget = CKTextAreaWidget()

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(255))
    subtitle = db.Column(db.String(255))
    category = db.Column(db.String(255))
    subcategory = db.Column(db.String(255))
    content = db.Column(db.Text)
    author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime)
    slug = db.Column(db.String(255))

# admin view that contains login 
class SecureModelView(ModelView):
    # Override is_accesible method - within module, simply returns true by default
    def is_accessible(self):
        if "logged_in" in session:
            return True
        else:
            abort(403)
    extra_js = ['//cdn.ckeditor.com/4.6.0/standard/ckeditor.js']

    form_overrides = {
        'content': CKTextAreaField
    }

    form_choices = {
    'category': [
        ('community_ed', 'Community Education'),
        ('ems_disaster', 'EMS and Disaster'),
        ('tactical_med', 'Tactical Medicine'),
        ('wilderness_med', 'Wilderness Medicine')
    ], 
    'subcategory': [
        ('no_subcategory', 'None'),
        ('care_other', 'Care of Others'),
        ('self_care', 'Self Care')
    ]
    }
         

# Model View for posts class
admin.add_view(SecureModelView(Posts, db.session))


#################################################
# Flask Routes
#################################################

# Homepage route
@app.route("/")
def homepage():
    # List all posts on homepage list
    posts = Posts.query.order_by(Posts.date_posted.desc())

    # Pagination logic
    # If there is a query string in the URL, request.args.get will grab the relevant defined variables
    # i.e. localhost:5000/?page=[something]
    page = request.args.get('page')

    # Check if page is a digit - if so, convert to int. Otherwise, default to 1
    if page and page.isdigit():
        page = int(page)
    else: 
        page = 1

    # Use built in paginate() method to create pages - ***update per_page argument after testing***
    pages = posts.paginate(page=page, per_page = 5)

    return render_template("index.html", posts=posts, pages=pages)

# About page route
@app.route("/about")
def about():
    return render_template("about.html")

# Post page route
@app.route("/post/<string:slug>")
def post(slug):
    try:
        post = Posts.query.filter_by(slug=slug).one()
        return render_template("post.html", post = post)
    except sqlalchemy.orm.exc.NoResultFound:
        abort(404)

# Contact page route
@app.route("/contact", methods=["GET","POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        message = request.form.get("message")
        email_body = f"Name: {name}\nE-mail: {email}\nPhone: {phone}\n\n\n{message}"

        msg = Message(subject=f"Mail from {name}", body=email_body, sender=mail_username, recipients=["jeremybar32093@gmail.com"])
        mail.send(msg)
        return render_template("contact.html", success=True)

    return render_template("contact.html")

# Login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Right now, handles only 1 user (admin user)
        # ***** FUTURE ENHANCEMENT - ADD ABILITY FOR MULTIPLE USER SIGNUP *****
        if request.form.get("username") == "admin" and request.form.get("password") == "$MedicineWithout2021$":
            session['logged_in'] = True
            return redirect("/admin")
        else:
            return render_template("login.html", failed=True)
    return render_template("login.html")

# Logout page
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# Contributors page
@app.route("/contributors")
def contributors():
    return render_template("contributors.html")

# Community Education page
@app.route("/community-education")
def community_education():
    posts = Posts.query.filter_by(category="community_ed").order_by(Posts.date_posted.desc())
    # Pagination logic
    # If there is a query string in the URL, request.args.get will grab the relevant defined variables
    # i.e. localhost:5000/?page=[something]
    page = request.args.get('page')

    # Check if page is a digit - if so, convert to int. Otherwise, default to 1
    if page and page.isdigit():
        page = int(page)
    else: 
        page = 1

    # Use built in paginate() method to create pages - ***update per_page argument after testing***
    pages = posts.paginate(page=page, per_page = 5)

    return render_template("community_education.html", posts=posts, pages=pages)

# EMS & Disaster page
@app.route("/ems-and-disaster")
def ems_disaster():
    posts = Posts.query.filter_by(category="ems_disaster").order_by(Posts.date_posted.desc())
    # Pagination logic
    # If there is a query string in the URL, request.args.get will grab the relevant defined variables
    # i.e. localhost:5000/?page=[something]
    page = request.args.get('page')

    # Check if page is a digit - if so, convert to int. Otherwise, default to 1
    if page and page.isdigit():
        page = int(page)
    else: 
        page = 1

    # Use built in paginate() method to create pages - ***update per_page argument after testing***
    pages = posts.paginate(page=page, per_page = 5)

    return render_template("ems_disaster.html", posts=posts, pages=pages)

# Wilderness Medicine page
@app.route("/wilderness-medicine")
def wilderness_medicine():
    posts = Posts.query.filter_by(category="wilderness_med").order_by(Posts.date_posted.desc())
    # Pagination logic
    # If there is a query string in the URL, request.args.get will grab the relevant defined variables
    # i.e. localhost:5000/?page=[something]
    page = request.args.get('page')

    # Check if page is a digit - if so, convert to int. Otherwise, default to 1
    if page and page.isdigit():
        page = int(page)
    else: 
        page = 1

    # Use built in paginate() method to create pages - ***update per_page argument after testing***
    pages = posts.paginate(page=page, per_page = 5)

    return render_template("wilderness_medicine.html", posts=posts, pages=pages)
    


#################################################
# Run flask app
#################################################
if __name__ == '__main__':
    app.run(debug=True)