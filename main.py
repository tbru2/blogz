from flask import Flask, render_template, redirect, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI']= 'mysql+pymysql://blogz:12345@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

app.secret_key = 'sakljflkasfj'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    pub_date = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __init__(self, title, body, owner, pub_date=None):
        self.title = title
        self.body = body
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date
        self.pub_date = pub_date
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog',backref='owner')

    def __init__(self,username,password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'index', 'blog', 'newpost']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash('Logged In')
            return redirect('/')
        else:
            flash('User Password Incorrect, Or User Does Not Exist','error')

    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/')
        else:
            return "<h1>Duplicate user</h1>"
    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html',users=users)

@app.route('/newpost', methods=['POST', 'GET'])
def add_post():
    title_error=''
    text_error=''
    error_check = False
    if request.method == "POST":
        title = request.form['title']
        text = request.form['text']
        owner = User.query.filter_by(username=session['username']).first()

        new_blog = Blog(title,text, owner)
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
        return render_template('individual.html',title=title,body=text, owner=newblog_owner)
    else:
        return render_template('newpost.html')
        
@app.route('/blog')
def newpost():
    blogs = Blog.query.order_by(Blog.pub_date).all()
    users = User.query.filter_by(id=Blog.owner_id).all()
    if request.args.get('id'):
        id = int(request.args.get('id'))
        singleblog = Blog.query.filter_by(id=id).first()
        title = blogs[id-1].title
        body = blogs[id-1].body
        owner = blogs[id-1].owner.username
        return render_template('individual.html',singleblog=singleblog)
    
    elif request.args.get('user'):
        user_id = int(request.args.get('user'))
        user_blogs = Blog.query.filter_by(id=user_id).all()
        user_name = User.query.filter_by(id=user_id).first()
        return render_template('singleuser.html',user_blogs=user_blogs,user_name=user_name)


    return render_template('blog.html',blogs=blogs)

if __name__=="__main__":
    app.run()