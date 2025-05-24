from flask import Flask, render_template, request, url_for, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone, timedelta
from flask_login import LoginManager, UserMixin, login_user,current_user,logout_user,login_required
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'log_ins' #имя функции


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dscabskasbd238hjsdcj2760'
db = SQLAlchemy(app)


class Log(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nick = db.Column(db.String(20),unique=True,nullable=False)
    email = db.Column(db.String(30),nullable=False)
    psw = db.Column(db.String(60),nullable=False)
    date = db.Column(db.DateTime,default= lambda: datetime.now(timezone.utc) + timedelta(hours=3))


    def __repr__(self):
        return f'Log {self.id}'

class Posts(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(40),nullable=False)
    content = db.Column(db.Text,nullable=False)
    date = db.Column(db.DateTime,default= lambda: datetime.now(timezone.utc) + timedelta(hours=3))
    user_id = db.Column(db.Integer, db.ForeignKey('log.id'), nullable=False)
    author = db.relationship('Log', backref=db.backref('posts', lazy=True))

    def __repr__(self):
        return f'<Posts {self.id}>'
#
# class Likes(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer,db.ForeignKey('log.id'), nullable=False)
#     post_id = db.Column(db.Integer,db.ForeignKey('posts.id'), nullable=False)
#
#     user = db.relationship('Log', backref=db.backref('likes', lazy=True))
#     post = db.relationship('Posts', backref=db.backref('likes', lazy=True))
#
#     def __repr__(self):
#         return f'<Likes {self.id}>'



@login_manager.user_loader
def load_user(user_id):
    return Log.query.get(int(user_id))

#
# @app.route('/like', methods=['POST'])
# @login_required
# def like_post(post_id):
#     post = Posts.query.get_or_404(post_id)
#
#     existing_like = Likes.query.filter_by(user_id=current_user.id, post_id=post.id).first()
#     if not existing_like:
#         like = Likes(user_id=current_user.id, post_id=post.id)
#         db.session.add(like)
#         db.session.commit()
#
#     return redirect(request.referrer or url_for('home'))






@app.route('/', methods=['GET'])
def home():
    posts = Posts.query.order_by(Posts.id.desc()).all()
    return render_template('home.html', posts=posts)


@app.route('/post/<int:id>')#chek post
def post(id):
    post = Posts.query.get(id)
    return render_template('posts.html',post=post)



@app.route('/post/<int:id>/del')#delete post
def dele(id):
    posts = Posts.query.get_or_404(id)
    try:
        db.session.delete(posts)
        db.session.commit()
        flash('The post successfully deleted.', category='success')
        return redirect('/')
    except:
        db.session.rollback()
        flash('The post is not deleted.', category='error')
        return redirect('/')



@app.route('/register', methods=['GET','POST']) #sing_up
def register():
    if request.method == 'POST':
        nick = request.form['nick'].strip()
        email = request.form['email'].strip()
        psw = request.form['psw'].strip()
        if not nick or not email or not psw:
            flash('Please fill in all fields!', category='error')
            return redirect('/register')
        psw_hash = generate_password_hash(psw)
        log = Log(nick=nick, email=email, psw=psw_hash)
        try:
            db.session.add(log)
            db.session.commit()
            flash('You have successfully registered!', category='success')
            return redirect('/register')
        except:
            db.session.rollback()
            flash('Sorry.You are not registered.', category='error')
            return redirect('/register')
    else:
        return render_template('log_in.html')


@app.route('/sign', methods=['GET','POST']) #log_in
def sign():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['psw']
        user = Log.query.filter_by(email=email).first()

        if user and check_password_hash(user.psw, password):
            login_user(user)
            flash('Welcome back!', 'success')
            return redirect('/')
        else:
            flash('Wrong email or password!', 'error')
            return redirect('/sign')
    return render_template('sign_up.html')

@app.route('/logout')
def logout():
    logout_user()
    flash('Logged out successfully.', category='success')
    return redirect('/')



@app.route('/create_a_post',methods=["GET","POST"])
@login_required
def create_a_post():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        if not title or not content:
            flash('Please fill in all fields!', category='error')
            return redirect('/create_a_post')
        posts = Posts(title=title,content=content,user_id=current_user.id)

        try:
            db.session.add(posts)
            db.session.commit()
            flash('Your post has been added.', category='success')
            return redirect('/')
        except:
            db.session.rollback()
            flash('Sorry.Your post has not been added.Please try again.', category='error')
            return redirect('/create_a_post')
    else:
        return render_template("index.html")

@app.route('/personal',methods=['GET'])
def personality():
    posts = Posts.query.order_by(Posts.id.desc()).all()
    return render_template('personal.html',posts=posts)


if __name__ == '__main__':
    app.run()
