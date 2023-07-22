from flask import Flask, render_template, flash, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from webForms import *
from flask_login import UserMixin
from flask_login import UserMixin, login_user,LoginManager, login_required, logout_user, current_user 
from flask_ckeditor import CKEditor
from werkzeug.utils import secure_filename
import uuid
import os

#App and DBMS Configs
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:tiger@localhost/blogWebsite'
app.config['SECRET_KEY'] = 'passKey'
UPLOAD_FOLDER = 'static/userImg'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ckeditor = CKEditor(app) 
db = SQLAlchemy(app)
migrate = Migrate(app, db)


#Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


#Database Models
class Blogs(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    datePosted = db.Column(db.DateTime, default=datetime.now)
    slug = db.Column(db.String(255))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(100), nullable = False, unique=True)
    name = db.Column(db.String(100), nullable = False)
    email = db.Column(db.String(100), nullable = False, unique = True)
    profile_pic = db.Column(db.String(50), nullable = True)
    about_author = db.Column(db.Text(500), nullable = True)
    dateAdded = db.Column(db.DateTime, default=datetime.now)
    password_hash = db.Column(db.String(128))
    blogs_written = db.relationship('Blogs', backref = 'authorId')

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

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

#Home Page
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')


#User Register-> Login-> Dashboard-> Logout
@app.route('/register', methods=['GET', 'POST'])
def register():
    name = None
    email = None
    form = UserForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        about_author = form.about_author.data
        password_hash = form.password.data
        password_hash = generate_password_hash(password_hash, "sha256")
        emailS = Users.query.filter_by(email=email).first()
        userS = Users.query.filter_by( username=username).first()
        if emailS is None and userS is None:
            user = Users(name=name, email=email, about_author=about_author, password_hash=password_hash, username=username)
            db.session.add(user)
            db.session.commit()
            flash("Successfully Registered")
            return redirect(url_for('login'))
        else:
            flash("Username/Email already exists")
        form.name.data = ''
        form.email.data = ''
        form.password.data = ''
        form.username.data = ''
        form.about_author.data = ''
    return render_template('userRegister.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username = form.username.data).first()
        if user:
            if(check_password_hash(user.password_hash, form.password.data)):
                login_user(user)
                flash("Login Successful")
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong Password, Try Again")
        else:
            flash("Incorrect Username")
    return render_template('userLogin.html', form=form)

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = UserForm()
    id = current_user.id
    print(current_user.about_author)
    user_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        email = request.form['email']
        user = Users.query.filter_by(email=email).first()
        if user is None or user_to_update.email == email:
            user_to_update.name = request.form['name']
            user_to_update.username = request.form['username']
            user_to_update.email = request.form['email']
            user_to_update.about_author = request.form['about_author']
            user_to_update.profile_pic = request.files['profile_pic']
            filename = secure_filename(user_to_update.profile_pic.filename)
            filename = str(uuid.uuid1()) + "_" + filename
            filename = filename[-49:]
            user_to_update.profile_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            user_to_update.profile_pic = filename
            db.session.commit()
            flash("User updated Successfully")
            return render_template('userDashboard.html', form=form)
        else:
            flash("User Email Already Exists!!!!")
            return render_template('userDashboard.html', form=form)
    else:
        return render_template('userDashboard.html', form=form)
    
@app.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def deleteUser(id):
    if id == current_user.id:
        user_to_delete = Users.query.get_or_404(id)
        try:
            db.session.delete(user_to_delete)
            db.session.commit()
            flash("User deleted successfully")
            return redirect('/login')
        except:
            flash("Error Deleting User!")
            return redirect('/dashboard')
    else:
        flash("You can't delete other user profile")
        return redirect('/dashboard')
 
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You have logged out successfully")
    return redirect(url_for('login'))


#Blogs - View, SoloView, Create, Edit, Update
@app.route('/blogs')
def blogs():
    blogs = Blogs.query.order_by(Blogs.datePosted)
    return render_template("blogs.html", blogs=blogs)

@app.route('/addBlog', methods=['GET', 'POST'])
@login_required
def addBlogs():
    form = BlogForm()
    if form.validate_on_submit():
        author = current_user.id
        title = form.title.data
        content = form.content.data
        slug = form.slug.data
        blog = Blogs(title=title, content=form.content.data, slug=slug, author_id=author)
        form.title.data = ''
        form.content.data = ''
        form.slug.data = ''
        db.session.add(blog)
        db.session.commit()
        flash("Blog Post Success")
        return redirect(url_for('blogs'))
    return render_template('addBlog.html', form=form)


@app.route('/blog/<int:id>')
def viewBlog(id):
    blog = Blogs.query.get_or_404(id)
    return render_template('viewBlog.html', blog=blog)

@app.route('/blog/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def editBlog(id):
    blog_to_update = Blogs.query.get_or_404(id)
    form = BlogForm()
    blog = Blogs.query.get_or_404(id)
    if form.validate_on_submit():
        blog_to_update.title = form.title.data
        blog_to_update.slug = form.slug.data
        blog_to_update.content = form.content.data

        db.session.add(blog_to_update)
        db.session.commit()
        flash("Blog Updated Successfully")
        return redirect(url_for('viewBlog', id=blog_to_update.id))
    if current_user.id == blog.authorId.id:
        form.title.data = blog_to_update.title
        form.slug.data = blog_to_update.slug
        form.content.data = blog_to_update.content
        return render_template("editBlog.html", form=form, id=id, blog=blog)
    else:
        flash("You can't edit this post")
        return redirect(url_for('viewBlog', id=blog.id))
    
@app.route('/blog/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def deleteBlog(id):
    form = BlogForm()
    blog = Blogs.query.get_or_404(id)
    id = current_user.id
    if id == blog.authorId.id:
        try:
            db.session.delete(blog)
            db.session.commit()
            flash("Blog deleted successfully")
            return redirect(url_for('blogs'))
        except:
            flash("Error Deleting Blog!")        
            return redirect(url_for('blogs'))
    else:
            flash("You can't delete this blog post")
            return redirect(url_for('blogs'))

