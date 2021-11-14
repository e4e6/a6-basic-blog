import os
from flask import Flask, render_template, redirect, url_for, flash,request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from flask_wtf import FlaskForm
from wtforms import SubmitField,StringField
from flask_migrate import Migrate
from wtforms.fields.simple import PasswordField, TextAreaField
from wtforms.form import Form
from wtforms.validators import DataRequired ,ValidationError, EqualTo, Length
from flask_login import LoginManager ,UserMixin ,current_user, login_user, logout_user, login_url
from datetime import datetime




basedir=os.path.abspath(os.path.dirname(__file__))

app=Flask(__name__)

app.config['SECRET_KEY']='secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db=SQLAlchemy(app)
migrate=Migrate(app,db)
login=LoginManager(app)
login.login_view = 'loginF'





# models
class Posts(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(20))
    text=db.Column(db.Text)
    created_date=db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'),
        nullable=False)
    #author=db.Column(db)
    
    
    
    
    
    
class User(UserMixin, db.Model):
    __name__='user'
    user_id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(32),nullable=False,unique=True)
    hashed_password=db.Column(db.String(256),nullable=False)
    post_ = db.relationship('Posts', backref='user', lazy=True)

    
    def turn_pass(self,password):
        self.hashed_password=generate_password_hash(password)
    
    def chk_pass(self,password):
        return check_password_hash(self.hashed_password,password)
    
    def get_id(self):   # normalde id olsa otomatik kullanılıyormuş flask_login için fakat farklı olunca tanımlamak gerekti
        return self.user_id
        
@login.user_loader
def load_user(id):
    return User.query.get(int(id))

# forms

class Register_form(FlaskForm):
    username=StringField(label='Username',validators=[DataRequired(message='username cant be empty')])
    password=PasswordField(label='Password',validators=[DataRequired(message='password cant be empty')])
    password_confirm=PasswordField(label='Password Confirm',validators=[DataRequired(message='password cant be empty'),EqualTo('password',message='passwords did not match')])
    submit=SubmitField('submit')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')
        
class Login_form(FlaskForm):
    username=StringField(label='Username',validators=[DataRequired(message='username cant be empty')])
    password=PasswordField(label='Password',validators=[DataRequired(message='password cant be empty')])
    submit=SubmitField('Submit')
    
class Post_form(FlaskForm):
    title=StringField(label='Title',validators=[DataRequired(message='title cant be empty')])# max 20
    text=TextAreaField(label='Text',validators=[DataRequired(message='text cant be empty')])# 
    submit=SubmitField(label='Submit')
    

# views

@app.route('/')
def indexF():
    posts=Posts.query.order_by(Posts.created_date.desc()).all()
    return render_template('index.html',posts=posts)

@app.route('/register', methods=['GET','POST'])
def registerF():
    form=Register_form()
    if form.validate_on_submit():        
        user=User()
        user.username=form.username.data
        user.turn_pass(form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('indexF'))
    return render_template('register.html',form=form)

@app.route('/login',methods=['GET','POST'])
def loginF():
    form=Login_form()
    if form.validate_on_submit():
        user=User.query.filter_by(username=form.username.data).first()
        if user and user.chk_pass(form.password.data) : 
            login_user(user) 
            return redirect(url_for('indexF')) 
        else :
            flash('Invalid username or password')
            return redirect(url_for('loginF'))
            
    return render_template('login.html',form=form)

@app.route('/logout')
def logoutF():
    logout_user()
    return redirect(url_for('indexF'))

@app.route('/addpost', methods=['GET','POST'])
def addpostF():
    form=Post_form()
    if form.validate_on_submit():
        post=Posts()
        post.title=form.title.data
        post.text=form.text.data
        post.user_id=current_user.user_id
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('indexF'))
    return render_template('addpost.html',form=form)

@app.route('/deletepost/<int:post_id>',methods=['POST'])
def deletepost(post_id):
    if request.method=='POST':
        post=Posts.query.filter_by(id=post_id).first()
        db.session.delete(post)
        db.session.commit()
        return redirect(url_for('indexF'))
    return redirect(url_for('indexF'))