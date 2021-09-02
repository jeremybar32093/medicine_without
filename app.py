#################################################
# Flask Setup
#################################################
import os
from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    redirect)
from flask_sqlalchemy import SQLAlchemy

#################################################
# Flask Setup
#################################################
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@localhost:5432/medicine_without"
db = SQLAlchemy(app)

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


#################################################
# Flask Routes
#################################################

# Homepage route
@app.route("/")
def homepage():
    return render_template("index.html")

# About page route
@app.route("/about")
def about():
    return render_template("about.html")

# Post page route
@app.route("/post")
def post():
    return render_template("post.html")

# Contact page route
@app.route("/contact")
def contact():
    return render_template("contact.html")


#################################################
# Run flask app
#################################################
if __name__ == '__main__':
    app.run(debug=True)