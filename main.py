from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI']= 'mysql+pymysql://build-a-blog:12345@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/')
def index():
    return render_template('newpost.html')

@app.route('/newpost', methods=['POST', 'GET'])
def add_post():
    title_error=''
    text_error=''
    error_check = False
    if request.method == "POST":
        title = request.form['title']
        text = request.form['text']

        new_blog = Blog(title,text)
        db.session.add(new_blog)
        db.session.commit()
        if title=='':
            title_error = "Please Enter A Title"
            error_check = True
        if text == '':
            text_error = "No Text Entered"
            error_check = True
        if error_check == True:
            return render_template('newpost.html',title_error=title_error,text_error=text_error)
        return render_template('individual.html',title=title,body=text)
    else:
        return render_template('newpost.html')
@app.route('/blog')
def newpost():
    blogs = Blog.query.all()
    if request.args.get('id'):
        id = int(request.args.get('id'))
        title = blogs[id-1].title
        body = blogs[id-1].body
        return render_template('individual.html',title=title,body=body)
    return render_template('blog.html',blogs=blogs)

if __name__=="__main__":
    app.run()