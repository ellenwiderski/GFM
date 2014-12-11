from flask import Flask, request, render_template, redirect, flash
from flask.ext.wtf import Form
from wtforms import TextField, PasswordField, IntegerField, BooleanField
from wtforms.validators import InputRequired
import sqlite3

app = Flask(__name__)
app.debug = True   # need this for autoreload and stack trace
app.config.from_object('config')

conn = sqlite3.connect("xmasapp.db") #create a connection (most databases are a client-server relationship, where requests are being sent and received
curs = conn.cursor() #cursor is the position or what row we are on in the db - a pointer to where we are in the db

class LoginForm(Form):
	username = TextField('Username',validators=[InputRequired()])
	password = PasswordField('Password',validators=[InputRequired()])

class SignupForm(Form):
	username = TextField('Username',validators=[InputRequired()])
	password = PasswordField('Password',validators=[InputRequired()])
	retypepassword = PasswordField('RetypePassword',validators=[InputRequired()])
	display_name = TextField('DisplayName',validators=[InputRequired()])
	age = IntegerField('Age',validators=[InputRequired()])
	naughty = BooleanField('Naughty')


@app.route('/', methods=['GET','POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		username = form.username.data
		password = form.password.data
		user = curs.execute('''SELECT user_name FROM user WHERE user_name = '%s' and password = '%s';'''% (username,password))
		hasUser = False
		for i in user:
			hasUser = True
		if not hasUser:
			return render_template('login.html',form=form)
		else:
			return redirect('/user/%s' % username)

	return render_template('login.html',form=form)

@app.route('/user/<username>', methods=['GET','POST'])
def profile(username):
	listdict = {}
	lists = curs.execute('''SELECT list.list_id FROM user, list WHERE list.user_name = user.user_name and list.user_name='%s';'''%username)
	for list in lists:
		items = curs.execute('''SELECT item.item_name, item.item_price, item.item_link from item, list, list_item WHERE list_item.list_item_id = list.list_id and list.list_id = '%s';'''%list[0])
		listdict[list[0]] = items
	return render_template('profile.html',listdict=listdict)

@app.route('/signup',methods=['GET','POST'])
def signup():
	form = SignupForm()
	if form.validate_on_submit():
		username = form.username.data
		password = form.password.data
		display_name = form.display_name.data
		age = form.age.data
		if form.naughty.data:
			naughty = 1
		else:
			naughty = 0

		user = curs.execute('''SELECT user_name FROM user WHERE user_name = '%s';'''% username)
		hasUser = False
		for i in user:
			hasUser = True
		if not hasUser:
			curs.execute('''INSERT INTO user values('%s','%s','%s',%s,%s);'''%(username,password,display_name,age,naughty))
			conn.commit()
			return redirect('/user/%s' % username)
		else:
			return render_template('signup.html',form=form)

	return render_template('signup.html',form=form)

if __name__ == '__main__':
   	app.run()