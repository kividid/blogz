from flask import Flask, redirect, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
import datetime
from passlib.hash import pbkdf2_sha256

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


@app.route('/blog')
def blog():
    args = request.args
    if 'id' in args:
        id = args['id']
        post = Blog.query.get(id)
        return render_template('singleblog.html', title=post.title, post=post)

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
            post = Blog(title, content)
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
        if not password:
            flash('Please enter a password')
            error = True
        elif not password == verify:
            flash('Passwords do not match')
            error = True
        if not email:
            flash('Please enter an email')
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

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():

    return render_template('login.html')


@app.route('/', methods=['GET', 'POST'])
def index():

    return render_template('index.html')


if __name__ == '__main__':
    app.run()
