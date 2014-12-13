from flask import Flask, flash, request, make_response, render_template, redirect, flash, g
from flask.ext.wtf import Form
from flask.ext.login import LoginManager, login_user, UserMixin, logout_user, login_required, current_user, AnonymousUserMixin
from wtforms import TextField, PasswordField, IntegerField, BooleanField, RadioField, SelectField
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

class Anonymous(AnonymousUserMixin):
  def __init__(self):
    self.username = 'Guest'

login_manager.anonymous_user = Anonymous

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
	name = TextField('additem',validators=[InputRequired()])
	forList = SelectField('forList')

class NewList(Form):
	name = TextField('newlist',validators=[InputRequired()])


@app.route('/user/<username>', methods=['GET','POST'])
@login_required
def profile(username):
	user = load_user(username)

	newitem = NewItem()
	newlist = NewList()

	listdict = {}
	choices = []

	lists = curs.execute('''SELECT list.list_id,list.list_name FROM user, list WHERE list.user_name = user.user_name and list.user_name='%s';'''%username)
	mylists = []

	for mylist in lists:
		mylists.append(mylist)

	for mylist in mylists:
		choices.append((mylist[1],mylist[1]))

		items = curs.execute('''SELECT item.item_name, item.item_price, item.item_link from item, list, list_item WHERE list_item.list_id = list.list_id and list.list_id = '%s';'''%mylist[0])
		
		listitems = []

		for item in items:
			listitems.append(item)

		listdict[mylist[1]] = listitems

	newitem.forList.choices = choices

	if newitem.validate_on_submit():
		c = curs.execute('''SELECT list_id FROM list ORDER BY list_id DESC''')
		highest = c.fetchone()[0]
		curs.execute('''INSERT into item values('%s',50,'amazon.com')''' % newitem.name.data)
		curs.execute('''INSERT into list_item values('%s',%s) '''%(newitem.name.data,highest+1))
		conn.commit()
		return redirect('/user/%s' % username)

	if newlist.validate_on_submit() :
		c = curs.execute('''SELECT list_id FROM list ORDER BY list_id DESC''')
		highest = c.fetchone()[0]
		curs.execute('''INSERT INTO list values(%s, '%s','%s')''' % (highest+1,newlist.name.data,username))
		conn.commit()
		return redirect('/user/%s' % username)

	return render_template('profile.html',
		listdict=listdict,
		newitem=newitem,
		newlist=newlist,
		curruser=current_user.username,
		profileuser=username,
		curruserdisplay = current_user.display_name,
		profileuserdisplay=user.display_name)


@app.route('/', methods=['GET','POST'])
def index():
	if current_user.username != 'Guest':
		return redirect('/user/%s' % current_user.username)
	return redirect('/login')

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
				return redirect("/user/%s" % g.user)

			else:
				return 'Incorrect password'
		else:
			return 'User does not exist'

	return render_template('login.html',form=form,curruser=current_user)

@app.route('/logout', methods=['GET','POST'])
def logout():
	logout_user()
	return redirect('/')

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
			return render_template('signup.html',form=form,curruser=current_user)

	return render_template('signup.html',form=form,curruser=current_user)

if __name__ == '__main__':
   	app.run()