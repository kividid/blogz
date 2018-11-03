from flask import Flask, redirect, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:Or.r0cks@localhost:8889/build-a-blog'
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

    def __init__(self, title, content):
        self.title = title
        self.content = content

    def __repr__(self):
        return '<Post {0}, {1}>'.format(self.title, self.id)


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


app.run()
