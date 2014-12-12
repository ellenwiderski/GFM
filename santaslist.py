from flask import Flask, flash, request, make_response, render_template, redirect, flash, g
from flask.ext.wtf import Form
from flask.ext.login import LoginManager, login_user, UserMixin, logout_user
from wtforms import TextField, PasswordField, IntegerField, BooleanField, RadioField
from wtforms.validators import InputRequired
import sqlite3

app = Flask(__name__)
app.debug = True   # need this for autoreload and stack trace
app.config.from_object('config')

login_manager = LoginManager()
login_manager.init_app(app)

conn = sqlite3.connect("xmasapp.db",check_same_thread = False) 
curs = conn.cursor()

class User(UserMixin):

    def __init__(self,username,password,display_name,naughty):
        self.username = username
        self.password = password
        self.display_name = display_name
        self.naughty = naughty

    def get_id(self):
    	try:
    		return self.username

    	except AttributeError:
    		raise NotImplementedError('No `id` attribute - override `get_id`')

    def __repr__(self):
        return '<User %s>' % (self.username)

    def add(self):
        c = curs.execute('''INSERT INTO user values('%s','%s','%s',%s);'''%(self.username,self.password,self.display_name,self.naughty))
        conn.commit()


@login_manager.user_loader
def load_user(username):
    c = curs.execute('''SELECT user_name,password,display_name,naughty from user where user_name = '%s' ''' % username)
    userrow = c.fetchone()
    user = User(userrow[0],userrow[1],userrow[2],userrow[3])
    return user

class LoginForm(Form):
	username = TextField('Username',validators=[InputRequired()])
	password = PasswordField('Password',validators=[InputRequired()])
	remember = BooleanField('remember')

class SignupForm(Form):
	username = TextField('Username',validators=[InputRequired()])
	password = PasswordField('Password',validators=[InputRequired()])
	retypepassword = PasswordField('RetypePassword',validators=[InputRequired()])
	display_name = TextField('DisplayName',validators=[InputRequired()])
	naughtynice = RadioField('NaughtyOrNice',choices=[('naughty','Naughty'),('nice','Nice')],validators=[InputRequired()])

class NewItem(Form):
	newitem = TextField('additem')


@app.route('/login', methods=['GET','POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		g.user = form.username.data
		g.password = form.password.data

		c = curs.execute('''SELECT user_name FROM user WHERE user_name = '%s';''' % g.user)
		userexists = c.fetchone()
		if userexists:
			c = curs.execute('''SELECT password FROM user WHERE password = '%s';''' % g.password)
			correct = c.fetchone()
			if correct:
				user = load_user(g.user)
				login_user(user, remember=form.remember.data)
				flash("logged in")
				return redirect("/user/%s" % g.user)

			else:
				return 'Incorrect password'
		else:
			return 'User does not exist'

	return render_template('login.html',form=form)

@app.route('/user/<username>', methods=['GET','POST'])
@login_required
def profile(username):

	form = NewItem()
	listdict = {}
	lists = curs.execute('''SELECT list.list_id FROM user, list WHERE list.user_name = user.user_name and list.user_name='%s';'''%username)
	for list in lists:
		items = curs.execute('''SELECT item.item_name, item.item_price, item.item_link from item, list, list_item WHERE list_item.list_id = list.list_id and list.list_id = '%s';'''%list[0])
		for item in items:
			listdict[list[0]] = item[0]
		
		# if form.validate_on_submit():
		# 	curs.execute('''INSERT into item values(form.newitem.data,50,"amazon.com")''')
		# 	items = curs.execute('''SELECT list_item_id FROM list_item ORDER BY list_item_id DESC''')
		# 	for i in items:
		# 		highest = i[0]

		# 	curs.execute('''INSERT into list_item values(%s,'%s',%s'''%(highest+1,form.newitem.data,listid))

		# if i[0] == cookieusername:
		# 	return render_template('profile.html',listdict=listdict,form=form,isUser=True)
		# else:
		# 	return render_template('profile.html',listdict=listdict,form=form,isUser=False)

	return render_template('profile.html',listdict=listdict,form=form)

@app.route('/signup',methods=['GET','POST'])
def signup():
	form = SignupForm()

	if form.validate_on_submit():
		user = form.username.data
		password = form.password.data
		display_name = form.display_name.data

		if form.naughtynice.data == 'naughty':
			naughty = 1
		else:
			naughty = 0

		c = curs.execute('''SELECT user_name FROM user WHERE user_name = '%s';'''% user)
		userexists = c.fetchone()

		if not userexists:
			newuser = User(user,password,display_name,naughty)
			newuser.add()
			return redirect('/user/%s' % user)
		else:
			return render_template('signup.html',form=form)

	return render_template('signup.html',form=form)

if __name__ == '__main__':
   	app.run()