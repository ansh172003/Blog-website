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



class Blogs(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    author = db.Column(db.String(255))
    datePosted = db.Column(db.DateTime, default=datetime.now)
    slug = db.Column(db.String(255))


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
    form = UserForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password_hash = form.password.data
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
        form.password.data = ''
        form.username.data = ''
    return render_template('userRegister.html', form=form)

@app.route('/blogs')
def blogs():
    blogs = Blogs.query.order_by(Blogs.datePosted)
    return render_template("blogs.html", blogs=blogs)

@app.route('/addBlog', methods=['GET', 'POST'])
def addBlogs():
    form = BlogForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        author = form.author.data
        slug = form.slug.data
        blog = Blogs(title=title, content=form.content.data, author=author, slug=slug)
        form.title.data = ''
        form.content.data = ''
        form.author.data = ''
        form.slug.data = ''
        db.session.add(blog)
        db.session.commit()
        flash("Blog Post Success")
    return render_template('addBlog.html', form=form)


@app.route('/blog/<int:id>')
def viewBlog(id):
    blog = Blogs.query.get_or_404(id)
    return render_template('viewBlog.html', blog=blog)

@app.route('/blog/edit/<int:id>', methods=['GET', 'POST'])
def editBlog(id):
    blog_to_update = Blogs.query.get_or_404(id)
    form = BlogForm()
    if form.validate_on_submit():
        blog_to_update.title = form.title.data
        blog_to_update.author = form.author.data
        blog_to_update.slug = form.slug.data
        blog_to_update.content = form.content.data

        db.session.add(blog_to_update)
        db.session.commit()
        flash("Blog Updated Successfully")
        return redirect(url_for('viewBlog', id=blog_to_update.id))

    form.title.data = blog_to_update.title
    form.author.data = blog_to_update.author
    form.slug.data = blog_to_update.slug
    form.content.data = blog_to_update.content
    return render_template("editBlog.html", form=form, id=id)
    
@app.route('/blog/delete/<int:id>', methods=['GET', 'POST'])
def deleteBlog(id):
    form = BlogForm()
    blog = Blogs.query.get_or_404(id)
    try:
        db.session.delete(blog)
        db.session.commit()
        flash("BLog deleted successfully")
        return redirect(url_for('blogs'))
    except:
        flash("Error Deleting Blog!")        
        return redirect(url_for('blogs'))
