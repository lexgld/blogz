from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'iloveguacamole'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    password = db.Column(db.String(15))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password        

@app.before_request
def require_login():
    allowed_routes = ['login','list_blogs', 'index', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if not user:
            flash('Username does not exist. Please create an account.','error')
            return redirect('/login') 

        if user and user.password == password:
            session['username'] = username
            flash('You are logged in!','confirmation')
            return redirect('/newpost')
     
        else: 
            flash('Password is incorrect!', 'error')
            return redirect('/login') 
        
    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify_psw = request.form['verify_psw'] 

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            flash('Chosen username is already taken.','error')
            return redirect('/signup') 
        if username == '':
            flash('You cannot leave fields blank.','error')
            return render_template('signup.html')
        if len(username) <= 3 or len(username) > 15:
            flash('Username must be between 3 and 15 characters.','error')
            return render_template('signup.html')
     
        if password == '':
            flash('You must choose a password','error')
            return render_template('signup.html')
        if len(password) <= 3 or len(password) > 15:
            flash('Password must be between 3 and 15 characters.','error')
            return render_template('signup.html')
  
        if verify_psw == '':
            flash('You must verify your password.','error')
            return render_template('signup.html')

        if password != verify_psw:
            flash('Passwords do not match!','error')
            return redirect('/signup')  

        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')  
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/', methods=['POST', 'GET'])
def index():
    all_users = User.query.all()
    return render_template('index.html', title="Blog", all_users=all_users)

@app.route('/blog')
def list_blogs():
    post_id = request.args.get('id')
    user_id = request.args.get('owner_id')

    if (post_id):
        ind_entry = Blog.query.get(post_id)
        return render_template('entry_page.html', title="Blog", ind_entry=ind_entry)
    else:
        if (user_id):
            ind_user_posts = Blog.query.filter_by(owner_id=user_id)
            return render_template('author_page.html', title="Blog", posts = ind_user_posts)
        else:
            all_posts = Blog.query.all()
            return render_template('blog.html', title="Blog Entry", blog_posts=all_posts)



@app.route('/newpost', methods=['POST', 'GET'])
def new_post():

    if request.method == 'POST':     
        owner = User.query.filter_by(username=session['username']).first()  
        blog_title = request.form['blog-title']
        blog_body = request.form['blog-entry']
        title_error = ''
        body_error = ''

        if not blog_title:
            title_error = "Please enter a blog title"
        if not blog_body:
            body_error = "Please enter a blog entry"

        if not body_error and not title_error:

            new_entry = Blog(blog_title, blog_body, owner)     
            db.session.add(new_entry)
            db.session.commit()        
            return redirect('/blog?id={}'.format(new_entry.id)) 
        else:
            return render_template('newpost.html', title='New Entry', title_error=title_error, body_error=body_error, 
                blog_title=blog_title, blog_body=blog_body)
    
    return render_template('newpost.html', title='New Entry')

if  __name__ == "__main__":
    app.run()