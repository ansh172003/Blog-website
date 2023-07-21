from flask import Flask, render_template, flash, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from webForms import *
from flask_login import UserMixin



app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:tiger@localhost/blog_website'
app.config['SECRET_KEY'] = 'passKey'

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(100), nullable = False, unique=True)
    name = db.Column(db.String(100), nullable = False)
    email = db.Column(db.String(100), nullable = False, unique = True)
    dateAdded = db.Column(db.DateTime, default=datetime.now)
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute!!')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password) 

    def __repr__(self):
        return self.email

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    name = None
    email = None
    form = AddUserForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password_hash = form.password_hash.data
        password_hash = generate_password_hash(password_hash, "sha256")
        emailS = Users.query.filter_by(email=email).first()
        userS = Users.query.filter_by( username=username).first()
        if emailS is None and userS is None:
            user = Users(name=name, email=email, password_hash=password_hash, username=username)
            db.session.add(user)
            db.session.commit()
            flash("User Added Successfully")
        else:
            flash("User already exists")
        form.name.data = ''
        form.email.data = ''
        form.password_hash.data = ''
        form.username.data = ''
    return render_template('userRegister.html', form=form)
