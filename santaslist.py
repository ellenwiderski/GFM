from flask import Flask, request, render_template, redirect, flash
from flask.ext.wtf import Form
from wtforms import TextField, PasswordField
from wtforms.validators import InputRequired

app = Flask(__name__)
app.debug = True   # need this for autoreload and stack trace
app.config.from_object('config')

class LoginForm(Form):
	username = TextField('Username',validators=[InputRequired()])
	password = PasswordField('Password',validators=[InputRequired()])

@app.route('/', methods=['GET','POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		return render_template('index.html',username=form.username.data)
	return render_template('login.html',form=form)

if __name__ == '__main__':
   app.run()