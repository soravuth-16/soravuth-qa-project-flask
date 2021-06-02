#move to home

from app import*
from .model import *
from flask import render_template, request, flash, redirect, url_for, jsonify
from werkzeug.exceptions import abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import Form
from wtforms import TextField, TextAreaField, SubmitField, PasswordField
from wtforms.fields.html5 import EmailField
from wtforms import validators, ValidationError
import sqlalchemy
from sqlalchemy.sql.expression import cast
import bcrypt
from app.model import MKT_USER
#import libgravatar import Gravatar

class RegisterForm(Form):
    username = TextField("FullName",[validators.Required("Please enter your name.")])
    email = EmailField("Email",[validators.Required("Please enter email address."), validators.Email("Incorrect Email Address")])
    password = PasswordField("password",[validators.DataRequired("Please enter the password."),validators.Length(min=6, message="Password is requried to minimize length 6 characters.")])
    submit = SubmitField("Register")
    
    def validate_email(form, field):
        Email_val = field.data
        postObj = MKT_USER.query.filter_by(Email = Email_val)
        if postObj.first():
            raise ValidationError(f'Email {Email_val} already exist!')

@app.route('/register', methods = ['POST', 'GET'])
def register():
    form = RegisterForm()

    if request.method == 'POST':

        if form.validate() == True:
            FullName = request.form['username']
            Email = request.form['email']
            Password = request.form['password']
            Avatar = 'avatar'
            Password = generate_password_hash(Password, "sha256")  

            post_user = MKT_USER(FullName = FullName, Email = Email, Password = Password, Avatar = Avatar)
            db.session.add(post_user)
            db.session.commit()

            flash("You have successfully sign up!")
            return redirect(url_for('index'))

    return render_template('auth/register.html', form = form)

@app.route('/login', methods = ['POST', "GET"])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        userObj = MKT_USER.query.filter_by(Email = email).first()
    
        if check_password_hash(userObj.Password, password) == True:
            login_user(userObj)
            return redirect(url_for('index'))
        else:

            return f'this is else conditon'

    return render_template('auth/login.html')
