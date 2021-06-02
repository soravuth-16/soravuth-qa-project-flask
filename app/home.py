from app import*
from .model import *
from flask import render_template, request, flash, redirect, url_for, jsonify
from werkzeug.exceptions import abort
from flask_wtf import Form
from wtforms import TextField, TextAreaField, SubmitField
from wtforms import validators, ValidationError
import sqlalchemy
from sqlalchemy.sql.expression import cast
import bcrypt
from app import*
from sqlalchemy import*
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import TextField, TextAreaField, SubmitField, PasswordField
from wtforms.fields.html5 import EmailField
from hashlib import md5
from sqlalchemy.sql.expression import update
from sqlalchemy.sql import func
class RegisterForm(Form):
	username = TextField("FullName",[validators.Required("Please enter your name.")])
	email = EmailField("Email",[validators.Required("Please enter email address."), validators.Email("Incorrect Email Address")])
	password = PasswordField("Password",[validators.DataRequired("Please enter the password."),validators.Length(min=6, message="Password is requried to minimize length 6 characters.")])
	submit = SubmitField("Sign Up")
	
	def validate_email(form, field):
		
		Email_val = field.data
		
		postObj = MKT_USER.query.filter_by(Email = Email_val)
		
		if postObj.first():
			print(f">>>>>>>>>>>>>>>")
			raise ValidationError(f'Email {Email_val} already exist!')
			return False
		return True

@app.route('/Login', methods = ['POST', "GET"])
def login():
	error = None
	if request.method == 'POST':
		email = request.form['email']
		password = request.form['password']
		
		userObj = MKT_USER.query.filter_by(Email = email).first()
		if userObj is None:
			flash("You have nor registered an account, Please sign up!")
			return redirect(url_for('index'))
		if check_password_hash(userObj.Password, password) == True:
			login_user(userObj)
			flash("You have succesffully logged In.")
			return redirect(url_for('index'))
		else:
			error = "Incorrect Email or password"
			return render_template('auth/login.html', error = error)

	return render_template('auth/login.html', error = error)

@app.route('/Register', methods = ['POST', 'GET'])
def register():
	form = RegisterForm()

	if request.method == 'POST':
		print(f">>>>>>>>>>>>>>{form.validate()}")
		if form.validate() == True:
			print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
			FullName = request.form['username']
			Email = request.form['email']
			Password = request.form['password']
			print (f'------------------{Email}')
			Avatar = 'https://www.gravatar.com/'+md5(b'Email').hexdigest()
			Password = generate_password_hash(Password, "sha256")  
			
			post_user = MKT_USER(FullName = FullName, Email = Email, Password = Password, Avatar = Avatar)
			db.session.add(post_user)
			db.session.commit()

			flash("You have successfully sign up!")
			return redirect(url_for('index'))

	return render_template('auth/register.html', form = form)


@app.route('/All')
def all():
	questions= db.session. \
			query(MKT_QUESTION.ID, MKT_QUESTION.Title, MKT_QUESTION.Body, MKT_QUESTION.Tag, MKT_QUESTION.Created, MKT_QUESTION.BestAnswer, MKT_USER.FullName). \
			join(MKT_USER, MKT_USER.ID== MKT_QUESTION.User). \
			order_by(MKT_QUESTION.Created.desc()). \
			all()

	CountAnswer= db.session.query(MKT_QUESTION.ID)
	
	count = len(questions)
	print(f"----------{questions}")
	return render_template('home/index.html',questions=questions,count = count)

@app.route('/MostRecent')
def MostRecent():
	questions= db.session. \
			query(MKT_QUESTION.ID, MKT_QUESTION.Title, MKT_QUESTION.Body, MKT_QUESTION.Tag, MKT_QUESTION.Created, MKT_QUESTION.BestAnswer, MKT_USER.FullName). \
			join(MKT_USER, MKT_USER.ID== MKT_QUESTION.User). \
			order_by(MKT_QUESTION.Created.desc()). \
				limit(10).\
					all()
	count = len(questions)
	print(f"----------{questions}")
	return render_template('home/index.html',questions=questions,count = count)

class QuestionForm(Form):
   Title = TextField("Question Title",[validators.Required("Please enter Question title."), validators.Length(min=15,max=150, message="Question Title Cannot less than 15")])
   Body = TextAreaField("Question Body",[validators.Required("Please enter Question Body.")])
   Tag = TextField("Tag and Topic",[validators.Required("Please enter Tag and Topic. ")])
   Submit = SubmitField("Post My Question")

   def validate_Title(form, field):
   		Title = field.data
   		postObj = MKT_QUESTION.query.filter_by(Title=Title)

   		if postObj.first():
   			raise ValidationError(f'Question title {Title} already exist!')

@app.route('/Question/New', methods=['GET','POST'])
@login_required
def newPost():
	form = QuestionForm()
	if request.method=='POST':
		print(f'>>>>>>>>>>>>>>>>>>>>>>>>>>{form.validate()}')
		if form.validate() == True:
			print("---------------")

			Title = request.form['Title']
			Body = request.form['Body']
			Tag = request.form['Tag']
			Vot = 0
			User = current_user.get_id()
			BestAnswer = 0

			Question = MKT_QUESTION(Title,Body,Tag,Vot,User,BestAnswer)

			db.session.add(Question)
			db.session.commit()

			flash('Your Question added successfull')

			return redirect(url_for('index'))
	return render_template('question/create.html', form=form)

class QuestionFormAnswerAndComment(Form):
	Comment = TextAreaField('Leave a Comment')
	Answer = TextAreaField('Leave a answer')
 
@app.route('/Question/View/<int:questionID>/<questionTag>', methods=['GET','POST'])
def ViewQuestion(questionID="",questionTag="",check=""):
	form = QuestionFormAnswerAndComment()

	if questionID != '':

		objQuestion = db.session.query(MKT_QUESTION.ID, MKT_QUESTION.Title, MKT_QUESTION.Body, MKT_QUESTION.Tag, MKT_QUESTION.Created, MKT_QUESTION.Vote, MKT_QUESTION.User, MKT_USER.FullName,MKT_USER.Avatar). \
			join(MKT_USER, MKT_USER.ID== MKT_QUESTION.User).filter(MKT_QUESTION.ID == questionID)
		Obj = db.session.\
			query(MKT_QUESTION.ID, MKT_QUESTION.Title, MKT_QUESTION.Tag). \
			join(MKT_USER, MKT_USER.ID== MKT_QUESTION.User).filter(and_(MKT_QUESTION.Tag == questionTag,MKT_QUESTION.ID != questionID)).\
				limit(2).\
					all()
		vote = db.session.\
			query(MKT_VOTE.ID).filter(MKT_VOTE.Question==questionID).\
				all()
		print(f'>>>>>>>>>>>>>>{Obj}')
		User = current_user.get_id()
		objUser = db.session.query(MKT_USER.FullName, MKT_USER.Avatar).filter(MKT_USER.ID == User)
		user = ''
		avatar = ''
		for obj in objUser:	
			user = obj['FullName']
			avatar = obj['Avatar']
		print('------------------------',avatar)

		if objQuestion.first() is None:
			abort(404)

		User = current_user.get_id()

		#comment
		objQuestion = db.session.query(MKT_QUESTION.ID, MKT_QUESTION.Title, MKT_QUESTION.Body, MKT_QUESTION.Tag, MKT_QUESTION.Created, MKT_QUESTION.Vote, MKT_QUESTION.User, MKT_USER.FullName,MKT_USER.Avatar). \
			join(MKT_USER, MKT_USER.ID== MKT_QUESTION.User).filter(MKT_QUESTION.ID == questionID)
		comm = db.session.\
			query(MKT_COMMENT.ID, MKT_COMMENT.Question, MKT_COMMENT.Comment,MKT_COMMENT.Created,MKT_USER.FullName). \
			join(MKT_QUESTION, MKT_QUESTION.ID== MKT_COMMENT.Question).\
			join(MKT_USER, MKT_USER.ID == MKT_COMMENT.UserID).\
				filter(MKT_QUESTION.ID == questionID).\
					all()
		UserQ=0
		for QUser in objQuestion:
			UserQ = QUser[6]
			print(f'----{UserQ}')


		count_com = len(comm)
		#answer
		answ = db.session.\
			query(MKT_ANSWER.ID, MKT_ANSWER.QuestionID, MKT_ANSWER.Answer,MKT_ANSWER.Created,MKT_USER.FullName, MKT_QUESTION.BestAnswer). \
			join(MKT_QUESTION, MKT_QUESTION.ID== MKT_ANSWER.QuestionID).\
			join(MKT_USER, MKT_USER.ID == MKT_ANSWER.User).\
				filter(MKT_QUESTION.ID == questionID).\
					all()
		
		count_ans = len(answ)
		print('-=-=-=-=-=-===--=-=-',answ)
		print(count_ans)

		return render_template('question/index.html', form=form, questions = objQuestion,\
				 Obj=Obj, user = user, avatar = avatar,count_vote=len(vote),questionID=questionID,\
					 questionTag=questionTag, comment = comm, count_com =count_com, answer = answ, count_ans = count_ans,User = User,UserQ=UserQ)
	return redirect(url_for('index'))

@app.route('/Question/View/<int:questionID>/<questionTag>/Answer', methods=['GET','POST'])
@login_required
def answer(questionID="",questionTag=""):
	form = QuestionFormAnswerAndComment()
			
	if request.method == 'POST':
		if questionID is not None:
			objQuestion = db.session.query(MKT_QUESTION.ID, MKT_QUESTION.Title, MKT_QUESTION.Body, MKT_QUESTION.Tag, MKT_QUESTION.Created, MKT_QUESTION.Vote, MKT_USER.FullName). \
			join(MKT_USER, MKT_USER.ID== MKT_QUESTION.User).filter(MKT_QUESTION.ID == questionID)
			if objQuestion.first() is None:
				abort(404)

			#insert Answer
			QuestionID = questionID
			User = current_user.get_id()
			Answer = request.form['Answer']

			objUser = db.session.query(MKT_USER.FullName).filter(MKT_USER.ID == User)
			user = ''
			for obj in objUser:	
				user = obj['FullName']
			print('------------------------',user)
			objAnswer = MKT_ANSWER(QuestionID,Answer,User)
			db.session.add(objAnswer)
			db.session.commit()

			AnswerCount = db.session.\
			query(MKT_ANSWER.ID).filter(MKT_ANSWER.QuestionID==questionID).\
				all()

			flash('Your answer has successfully added!')
			
			return redirect(url_for('ViewQuestion',questionID=questionID,questionTag=questionTag,check=""))
	return redirect(url_for('ViewQuestion',questionID=questionID,questionTag=questionTag,check=""))
@app.route('/Logout')
def logout():
	logout_user()
	flash('You are now logout!')
	return redirect(url_for('index'))


@app.route('/Question/View/<int:questionID>/<questionTag>/Vote', methods=['GET','POST'])
@login_required
def VoteQuestion(questionID="",questionTag=""):
	user = current_user.get_id()
	Vote = MKT_VOTE(questionID,user)
	db.session.add(Vote)
	db.session.commit()

	vote = db.session.\
			query(MKT_VOTE.ID).filter(MKT_VOTE.Question==questionID).\
				all()

	data = db.session.query(MKT_QUESTION).filter(MKT_QUESTION.ID==questionID).first()
	data.Vote = len(vote)
	db.session.commit()
	db.session.flush()


	return redirect(url_for('ViewQuestion',questionID=questionID,questionTag=questionTag,check=""))

@app.route('/Question/View/<int:questionID>/<questionTag>/Comment', methods=['GET','POST'])
@login_required
def comment(questionID="",questionTag=""):
			
	if request.method == 'POST':

		#insert Comment
		QuestionID = questionID
		User = current_user.get_id()
		Comment = request.form['Comment']

		objComment = MKT_COMMENT(QuestionID,Comment,User)
		db.session.add(objComment)
		db.session.commit()
		
		flash('Your comment have successfully added!')
		
	return redirect(url_for('ViewQuestion',questionID=questionID,questionTag=questionTag,check=""))

@app.route('/Answer')
def ViewQuestionAnswer():
	subquery = db.session.query(MKT_ANSWER.QuestionID)

	objQuestion = db.session.query(MKT_QUESTION.ID, MKT_QUESTION.Title, MKT_QUESTION.Body, MKT_QUESTION.Tag, MKT_QUESTION.Created, MKT_USER.FullName). \
			join(MKT_USER, MKT_USER.ID== MKT_QUESTION.User).\
				order_by(MKT_QUESTION.Created.desc()). \
				filter(MKT_QUESTION.ID.in_(subquery))
	count = objQuestion.count()
	return render_template('home/index.html',questions=objQuestion,count = count)

@app.route('/Unanswer')
def ViewQuestionUnanswer():

	subquery = db.session.query(MKT_ANSWER.QuestionID)

	objQuestion = db.session.query(MKT_QUESTION.ID, MKT_QUESTION.Title, MKT_QUESTION.Body, MKT_QUESTION.Tag, MKT_QUESTION.Created, MKT_USER.FullName). \
			join(MKT_USER, MKT_USER.ID== MKT_QUESTION.User).\
				order_by(MKT_QUESTION.Created.desc()). \
				filter(MKT_QUESTION.ID.not_in(subquery))
	count = objQuestion.count()
	return render_template('home/index.html',questions=objQuestion,count = count)

@app.route('/Popular')
def Popular():
	questions= db.session. \
			query(MKT_QUESTION.ID, MKT_QUESTION.Title, MKT_QUESTION.Body, MKT_QUESTION.Tag, MKT_QUESTION.Created, MKT_QUESTION.BestAnswer, MKT_USER.FullName). \
			join(MKT_USER, MKT_USER.ID== MKT_QUESTION.User). \
			order_by(MKT_QUESTION.Vote.desc()). \
				limit(10).\
					all()
	count = len(questions)
	print(f"----------{questions}")
	return render_template('home/index.html',questions=questions,count = count)

@app.route('/Manager')
def Manager():
	user = current_user.get_id()

	objQuestion = db.session.query(MKT_QUESTION.ID, MKT_QUESTION.Title, MKT_QUESTION.Body, MKT_QUESTION.Tag, MKT_QUESTION.Created, MKT_QUESTION.BestAnswer). \
			join(MKT_USER, MKT_USER.ID== MKT_QUESTION.User).filter(MKT_QUESTION.User==user)
	objUser = MKT_USER.query.get(user)
	if objQuestion:

		return render_template('question/update.html', questions=objQuestion,User = objUser)
	else:
		return render_template('question/update.html', questions=[], User = [])

@app.route('/Question/<int:questionID>/Delete')
@login_required
def deletePost(questionID):
	if questionID:
		MKT_QUESTION.query.filter_by(ID=questionID).delete()
		db.session.commit()
		flash(f'Question {questionID} has been deleted successfull')
	return redirect(url_for('Manager'))


@app.route('/Question/<int:questionID>/Edit', methods=['GET','POST'])
@login_required
def editQuestion(questionID=''):

	form = QuestionForm()

	if request.method=='POST':
		objQuestion = MKT_QUESTION.query.\
		filter_by(ID=questionID).\
		first() #.update

		objQuestion.Title = request.form['Title']
		objQuestion.Body = request.form['Body']
		objQuestion.Tag = request.form['Tag']
		db.session.commit()
		return redirect(url_for('Manager'))

	if questionID:
		objQuestion = MKT_QUESTION.query.get(questionID)
		if objQuestion:
			form.Title.data = objQuestion.Title
			form.Body.data = objQuestion.Body
			form.Tag.data = objQuestion.Tag
			flash('Your Question have successfully updated!')
			return render_template('question/create.html', form=form)
	abort(404)


@app.route('/Question/View/<int:questionID>/<questionTag>/<int:answerID>/BestAnswer', methods = ['POST','GET'])
@login_required
def bestAnswer(questionID='', answerID = '',questionTag = ''):
	if questionID is not None:
		if request.form.getlist('checkBest'): #if checkbox is checked
			objAnswer = db.session.query(MKT_ANSWER.ID, MKT_ANSWER.Answer, MKT_ANSWER.User,MKT_USER.FullName). \
			join(MKT_USER, MKT_USER.ID== MKT_ANSWER.User).filter(MKT_ANSWER.ID == 1).all()
			#need to find answer ID
			ansID = answerID
			data = db.session.query(MKT_QUESTION).filter(MKT_QUESTION.ID==questionID).first()
			data.BestAnswer = ansID #true
			db.session.commit()
			db.session.flush()
			print('-------------------------',ansID)
			flash("You have successfully choose the best answer!")
			return redirect(url_for('ViewQuestion',questionID = questionID ,questionTag = questionTag,check="selected"))
	return redirect(url_for('ViewQuestion',questionID = questionID ,questionTag = questionTag,check=""))
