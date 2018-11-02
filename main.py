from flask import Flask, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:Or.r0cks@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True

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
        return '<Post %r>' % self.title


@app.route('/blog')
def blog():
    blogs = Blog.query.all()

    return render_template('blog.html', title='Blog', blogs=blogs)


@app.route('/newpost', methods=['GET', 'POST'])
def newpost():

    if request.method == 'POST':
        
        return redirect('blog.html')

    return render_template('newpost.html', title='Create New Post')


app.run()
