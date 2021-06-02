import datetime
from app import app, db,login_manager
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_login import UserMixin, login_user, login_required, logout_user,current_user
import bcrypt
from werkzeug.security import check_password_hash

#table MKT_USER
class MKT_USER(UserMixin,db.Model):
    ID = db.Column(db.Integer, primary_key = True)
    FullName= db.Column(db.String(50), nullable=False)
    Email = db.Column(db.String(75), nullable=False)
    Password = db.Column(db.String(150), nullable=False)
    Avatar = db.Column(db.String(100), nullable=False)
    Created = db.Column(db.String(20), default=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    def get_id(self):
        return self.ID

    def __init__(self, FullName, Email, Password, Avatar):
        self.FullName = FullName
        self.Email = Email
        self.Password = Password
        self.Avatar = Avatar

@login_manager.user_loader
def load_user(user_id):
   return MKT_USER.query.get(int(user_id))

#table MKT_QUESTION
class MKT_QUESTION(db.Model):
    ID = db.Column(db.Integer, primary_key = True)
    Title= db.Column(db.String(75), nullable=False)
    Body = db.Column(db.Text, nullable=False)
    Tag = db.Column(db.String(150), nullable=False)
    Vote = db.Column(db.Integer, nullable=False, default=0)
    User = db.Column(db.Integer, nullable=False)
    BestAnswer = db.Column(db.Integer)
    Created = db.Column(db.String(20), default=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


    def __init__(self, Title, Body, Tag, Vote, User,BestAnswer):
        self.Title = Title
        self.Body = Body
        self.Tag = Tag
        self.Vote = Vote
        self.User = User
        self.BestAnswer = BestAnswer
#TABLE MKT_ANSWER
class MKT_ANSWER(db.Model):
    ID = db.Column(db.Integer, primary_key = True)
    QuestionID= db.Column(db.Integer, nullable=False)
    Answer = db.Column(db.Text, nullable=False)
    User = db.Column(db.Integer, nullable=False)

    Created = db.Column(db.String(20), default=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


    def __init__(self, QuestionID, Answer, User):
        self.QuestionID = QuestionID
        self.Answer = Answer
        self.User = User

#TABLE VOTE
class MKT_VOTE(db.Model):
    ID = db.Column(db.Integer, primary_key = True)
    Question = db.Column(db.Integer, nullable=False)
    UserID = db.Column(db.Integer, nullable=False)

    Created = db.Column(db.String(20), default=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


    def __init__(self, Question, UserID):
        self.Question = Question
        self.UserID = UserID

#TABLE COMMENT
class MKT_COMMENT(db.Model):
    ID = db.Column(db.Integer, primary_key = True)
    Question= db.Column(db.Integer, nullable=False)
    Comment = db.Column(db.Text, nullable=False)
    UserID = db.Column(db.Integer, nullable=False)

    Created = db.Column(db.String(20), default=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


    def __init__(self, Question, Comment, UserID):
        self.Question = Question
        self.Comment = Comment
        self.UserID = UserID
    
