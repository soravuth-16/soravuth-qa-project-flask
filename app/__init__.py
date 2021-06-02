from flask import Flask, render_template
#from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from flask_login import LoginManager, UserMixin
import os

app = Flask(__name__)

app.config['SECRET_KEY']='!loveyou@ll'

DB_USER = 'users' # database user
DB_PWD = '12345'# database password
DB_NAME = 'qadb'
#hello
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://xwmloiowwgoahp:7878092489a2bebef7b6e21dafeb0185fcf8f6ecbf8a8cb5e4093a070f7515ee@ec2-54-145-224-156.compute-1.amazonaws.com:5432/ddl5s5r8bddcbj"
app.config['SQLALCHEMY_DATABASE_URI'] = os.environt.get('DATABASE_URL').replace("://","ql://",1)

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "login"
db = SQLAlchemy(app)
from .home import * 

@app.route('/',methods=['GET','POST'])
def index():
	Search = request.args.get('Search')
	print(f">>>>>>>>>>>>>>>>>>{Search}")
	if Search==None:
		questions= db.session. \
			query(MKT_QUESTION.ID, MKT_QUESTION.Title, MKT_QUESTION.Body, MKT_QUESTION.Tag, MKT_QUESTION.Created, MKT_QUESTION.BestAnswer, MKT_USER.FullName). \
			join(MKT_USER, MKT_USER.ID== MKT_QUESTION.User). \
				order_by(MKT_QUESTION.Created.desc()). \
					limit(10).\
						all()
		count = len(questions)
	else:
		search = f"%{Search}%"
		questions= db.session. \
			query(MKT_QUESTION.ID, MKT_QUESTION.Title, MKT_QUESTION.Body, MKT_QUESTION.Tag, MKT_QUESTION.Created, MKT_QUESTION.BestAnswer, MKT_USER.FullName). \
			join(MKT_USER, MKT_USER.ID== MKT_QUESTION.User). \
			order_by(MKT_QUESTION.Created.desc()). \
			filter(or_(MKT_QUESTION.Title.like ("%"f"{search}""%"),MKT_QUESTION.Body.like("%"f"{search}""%"),MKT_QUESTION.Body.like("%"f"{search}""%"))).\
				limit(10)
		
		count = questions.count()
	
	return render_template('home/index.html',questions=questions,count = count)

