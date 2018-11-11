from flask import Flask, redirect, render_template, request, flash, session
from flask_sqlalchemy import SQLAlchemy
import datetime
from passlib.hash import pbkdf2_sha256
import re

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:Or.r0cks@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = 'j5%NNapT*F5S60FrF1tP'

db = SQLAlchemy(app)


def _get_date():
    return datetime.datetime.now()


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    post_date = db.Column(db.DateTime, default=_get_date)
    content = db.Column(db.String(1000))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, content, author_id):
        self.title = title
        self.content = content
        self.author_id = author_id

    def __repr__(self):
        return '<Post {0}, {1}>'.format(self.title, self.id)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60))
    password_hash = db.Column(db.String(200))
    email = db.Column(db.String(60))
    blogs = db.relationship('Blog', backref='author')

    def __init__(self, username, password_hash, email):
        self.username = username
        self.password_hash = password_hash

    def __repr__(self):
        return '<User {0}>'.format(self.username)


@app.before_request
def require_login():
    allowed = ['signup', 'login', 'blog', 'index']
    if not ('user' in session or request.endpoint in allowed):
        return redirect("/blog")


@app.route('/blog')
def blog():
    args = request.args

    if 'id' in args:
        id = args['id']
        post = Blog.query.get(id)
        return render_template('singleblog.html', title=post.title, post=post)

    if 'user' in args:
        user_id = args['user']
        user = User.query.get(user_id)
        title = 'Posts by {}'.format(user.username)
        posts = Blog.query.order_by(Blog.post_date.desc()).filter_by(author_id=user_id).all()
        return render_template('singleUser.html', title=title, posts=posts, user=user)

    blogs = Blog.query.order_by(Blog.post_date.desc()).all()

    return render_template('blog.html', title='Blog', blogs=blogs)


@app.route('/newpost', methods=['GET', 'POST'])
def newpost():

    title = ''
    content = ''

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title or not content:
            flash('Please enter a title and some content for the blog post!', 'error')
        else:
            user = User.query.filter_by(username=session['user']).first()
            post = Blog(title, content, user.id)
            db.session.add(post)
            db.session.commit()

            return redirect('/blog?id={}'.format(post.id))

    return render_template('newpost.html', title='Create New Post', post_title=title, post_content=content)


@app.route('/signup', methods=['GET', 'POST'])
def signup():

    error = False
    username = ''
    email = ''

    if request.method == 'POST':
        username = request.form['user']
        password = request.form['pass']
        verify = request.form['pass2']
        email = request.form['email']

        if not username:
            flash('Please enter a user name')
            error = True
        elif len(username) < 3:
            flash('Username must be at least three characters')
        if not password:
            flash('Please enter a password')
            error = True
        elif len(password) < 3:
            flash('Password must be at least three characters')
            error = True
        elif not password == verify:
            flash('Passwords do not match')
            error = True
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Please enter a valid email')
            error = True

        existing = User.query.filter_by(username=username).first()

        if existing:
            flash('User already exists - please choose a unique user name')
            error = True

        if error is True:
            return render_template('signup.html', username=username, email=email)

        hash = pbkdf2_sha256.hash(password)

        new_user = User(username, hash, email)
        db.session.add(new_user)
        db.session.commit()

        session['user'] = username

        return redirect('/newpost')

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():

    username = ''

    if request.method == 'POST':
        username = request.form['user']
        password = request.form['pass']

        user = User.query.filter_by(username=username).first()

        if not user:
            flash('User does noe exist')
        else:
            hash = user.password_hash

            if not pbkdf2_sha256.verify(password, hash):
                flash('Incorrect password')
            else:
                session['user'] = username
                return redirect('/newpost')

    return render_template('login.html', username=username)


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/blog')


@app.route('/', methods=['GET', 'POST'])
def index():

    users = User.query.all()

    return render_template('index.html', users=users)


if __name__ == '__main__':
    app.run()
