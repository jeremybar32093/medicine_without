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

#################################################
# Flask Setup
#################################################
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@localhost:5432/medicine_without"
# Secret Key for being able to post back to database
app.config["SECRET_KEY"] = "$MedicineWithout2021$"
db = SQLAlchemy(app)
# Create admin page object
admin = Admin(app)

#################################################
# Database tables via classes
#################################################
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(255))
    subtitle = db.Column(db.String(255))
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
         

# Model View for posts class
admin.add_view(SecureModelView(Posts, db.session))


#################################################
# Flask Routes
#################################################

# Homepage route
@app.route("/")
def homepage():
    # List all posts on homepage list
    # *** FUTURE ENHANCEMENT - add pagination***
    posts = Posts.query.all()
    return render_template("index.html", posts = posts)

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
@app.route("/contact")
def contact():
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


#################################################
# Run flask app
#################################################
if __name__ == '__main__':
    app.run(debug=True)