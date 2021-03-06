from flask import Flask, flash, request, make_response, render_template, redirect, flash, g
from flask.ext.login import LoginManager, login_user, UserMixin, logout_user, login_required, current_user, AnonymousUserMixin
from flask.ext.wtf import Form
from wtforms import TextField, PasswordField, IntegerField, BooleanField, RadioField, SelectField
from wtforms.fields.html5 import URLField
from wtforms.validators import DataRequired, url, Optional
import psycopg2


app = Flask(__name__)
app.debug = True   # need this for autoreload and stack trace
app.config.from_object('config')

login_manager = LoginManager()
login_manager.init_app(app)

conn = psycopg2.connect(database="d4gnik1781p8qs", user="ecxyptlvfvtqfi", password="Iyi4Mc9aJEax2o_5tyIx1SKAGk", host="ec2-54-243-44-191.compute-1.amazonaws.com", port=5432)
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
        curs.execute('''INSERT INTO users 
        	values($$%s$$,$$%s$$,$$%s$$,$$%s$$);'''%(self.username,self.password,self.display_name,self.naughty))
        conn.commit()

class Anonymous(AnonymousUserMixin):
  def __init__(self):
    self.username = 'Guest'
    self.display_name = "Guest"

login_manager.anonymous_user = Anonymous

@login_manager.user_loader
def load_user(username):
    curs.execute('''SELECT user_name,password,display_name,naughty 
    	from users 
    	where user_name = $$%s$$ ''' % username)
    userrow = curs.fetchone()
    if userrow is not None:
    	user = User(userrow[0],userrow[1],userrow[2],userrow[3])
    
    else:
    	user = Anonymous()

    return user

class LoginForm(Form):
	username = TextField('Username',validators=[DataRequired()])
	password = PasswordField('Password',validators=[DataRequired()])
	remember = BooleanField('remember')

class SignupForm(Form):
	username = TextField('Username',validators=[DataRequired()])
	password = PasswordField('Password',validators=[DataRequired()])
	retypepassword = PasswordField('RetypePassword',validators=[DataRequired()])
	display_name = TextField('DisplayName',validators=[DataRequired()])
	naughtynice = RadioField('NaughtyOrNice',choices=[('naughty','Naughty'),('nice','Nice')],validators=[DataRequired()])

class NewItem(Form):
	name = TextField('additem',validators=[DataRequired()])
	forList = SelectField('forList')
	website = TextField('website')
	price = TextField('price')

class NewList(Form):
	name = TextField('newlist',validators=[DataRequired()])

class Search(Form):
	keyword = TextField('keyword',validators=[DataRequired()])


@app.route('/copy/<list_id>',methods=['GET','POST'])
def copy(list_id):
	curs.execute('''SELECT list_name FROM list WHERE list_id=%s'''%list_id)
	listname = curs.fetchone()[0]

	curs.execute(''' INSERT INTO list (list_name,user_name) values($$%s$$,$$%s$$) RETURNING list_id'''%(listname,current_user.username))
	listid = curs.fetchone()[0]

	curs.execute(''' SELECT * FROM list JOIN list_item USING(list_id) JOIN item USING(item_id) WHERE list_id=%s'''%list_id)
	c = curs.fetchall()
	
	for item in c:
		curs.execute(''' INSERT INTO list_item values(%s,%s)'''%(item[0],listid))

	return redirect('/')

@app.route('/deletelist/<list_id>',methods=['GET','POST'])
def deletelist(list_id):
	curs.execute('''DELETE FROM list_item WHERE list_item.list_id = $$%s$$ ''' % list_id)
	curs.execute('''DELETE FROM list WHERE list.list_id = %s''' % list_id)
	conn.commit()
	return redirect('/')

@app.route('/deleteitem/<list_id>/<item_id>',methods=['GET','POST'])
def deleteitem(list_id,item_id):
	curs.execute('''DELETE FROM list_item 
		WHERE list_item.item_id = %s 
		AND list_item.list_id = %s''' % (item_id,list_id))

	conn.commit()
	return redirect('/')

	

@app.route('/user/<username>', methods=['GET','POST'])
def profile(username):
	user = load_user(username)

	newitem = NewItem()
	newlist = NewList()
	search = Search()

	listdict = {}
	choices = []

	curs.execute('''SELECT list.list_id, list.list_name 
		FROM users JOIN list USING(user_name) 
		WHERE list.user_name=$$%s$$;'''%username)

	lists = curs.fetchall()
	mylists = []

	for mylist in lists:
		mylists.append(mylist)

	for mylist in mylists:
		choices.append((str(mylist[0]),mylist[1]))
		curs.execute('''SELECT item.item_name,item.item_link, item.item_id, item.item_price
			FROM item JOIN list_item USING(item_id) JOIN list USING(list_id) 
			WHERE list.list_id=%s;'''%mylist[0])

		items = curs.fetchall()

		listitems = []

		list_id = mylist[0]
		list_name = mylist[1]

		for item in items:
			listitems.append(item)

		listdict[list_id] = (list_name,listitems)

	newitem.forList.choices = choices

	if newitem.validate_on_submit():

		curs.execute('''SELECT item.item_name, item.item_price, item.item_link, item.item_id
			FROM item 
			WHERE item.item_name=$$%s$$ AND item.item_price=$$%s$$ AND item.item_link=$$%s$$ '''%(newitem.name.data,newitem.price.data,newitem.website.data))

		c = curs.fetchone()
		

		if c is None:
			curs.execute('''INSERT into 
				item (item_name,item_price,item_link)
				values($$%s$$,$$%s$$,$$%s$$) RETURNING item_id''' % (newitem.name.data,newitem.price.data,newitem.website.data))
		
			itemID = curs.fetchone()[0]

		else:
			itemID = c[3]

		listid = int(newitem.forList.data)
		
		curs.execute('''INSERT into list_item 
			values(%s,%s) '''%(itemID,listid))

		conn.commit()
		return redirect('/user/%s' % username)

	if newlist.validate_on_submit() :
		curs.execute('''INSERT INTO list (list_name,user_name) 
			values($$%s$$,$$%s$$)''' % (newlist.name.data,username))

		conn.commit()
		return redirect('/user/%s' % username)

	if search.validate_on_submit():
		return redirect('/search/%s'%search.keyword.data)

	profileuser=load_user(username)

	return render_template('profile.html',
		listdict=listdict,
		newitem=newitem,
		newlist=newlist,
		curruser=current_user.username,
		profileuser=profileuser,
		curruserdisplay = current_user.display_name,
		profileuserdisplay=user.display_name,
		search=search)


@app.route('/', methods=['GET','POST'])
def index():
	if current_user.username != 'Guest':
		return redirect('/user/%s' % current_user.username)
	return redirect('/login')

@app.route('/login', methods=['GET','POST'])
def login():
	form = LoginForm()
	search = Search()

	if form.validate_on_submit():
		g.user = form.username.data
		g.password = form.password.data

		curs.execute('''SELECT user_name 
			FROM users 
			WHERE user_name = $$%s$$;''' % g.user)

		c = curs.fetchone()
		if c is not None:
			curs.execute('''SELECT password 
				FROM users 
				WHERE password = $$%s$$;''' % g.password)

			correct = curs.fetchone()
			if correct:
				user = load_user(g.user)
				login_user(user, remember=form.remember.data)
				return redirect("/user/%s" % g.user)

			else:
				return render_template('login.html',
						form=form,
						curruser=current_user,
						search=search,
						validuser=False)
		else:
			return render_template('login.html',
						form=form,
						curruser=current_user,
						search=search,
						validuser=False)

	if search.validate_on_submit():
		return redirect('/search/%s'%search.keyword.data)

	return render_template('login.html',
		form=form,
		curruser=current_user,
		search=search,
		validuser=True)

@app.route('/logout', methods=['GET','POST'])
def logout():
	logout_user()
	return redirect('/')

@app.route('/signup',methods=['GET','POST'])
def signup():
	form = SignupForm()
	search = Search()

	if search.validate_on_submit():
		return redirect('/search/%s'%search.keyword.data)

	if form.validate_on_submit():
		user = form.username.data
		password = form.password.data
		retype = form.retypepassword.data
		display_name = form.display_name.data

		if password == retype:

			if form.naughtynice.data == 'naughty':
				naughty = 1
			else:
				naughty = 0

			curs.execute('''SELECT user_name 
				FROM users 
				WHERE user_name = $$%s$$;'''% user)

			c = curs.fetchone()
			if c is None:
				newuser = User(user,password,display_name,naughty)
				newuser.add()
				login_user(newuser)
				return redirect('/user/%s' % user)
			else:
				return render_template('signup.html',
					form=form,
					curruser=current_user,
					search=search,
					validuser=False,
					passmatch=True)

		else:
			return render_template('signup.html',
						form=form,
						curruser=current_user,
						search=search,
						validuser=True,
						passmatch=False)

	return render_template('signup.html',
			form=form,
			curruser=current_user,
			search=search,
			validuser=True,
			passmatch=True)


@app.route('/search/<keyword>', methods=['GET','POST'])
def search(keyword):
	search = Search()
	curs.execute(''' SELECT * 
		FROM list 
		WHERE list_name ILIKE '%{0}%' '''.format(keyword))

	c = curs.fetchall()
	lists = []
	for l in c:
		lists.append(l)

	curs.execute(''' SELECT item.item_name,list.list_name,list.user_name 
		FROM item JOIN list_item USING(item_id) JOIN list USING(list_id) 
		WHERE item_name ILIKE '%{0}%' '''.format(keyword))

	c = curs.fetchall()
	items = []
	for i in c:
		items.append(i)

	curs.execute(''' SELECT users.user_name, users.display_name 
		FROM users 
		WHERE user_name ILIKE '%{0}%' 
		OR display_name ILIKE '%{0}%'; '''.format(keyword))

	c = curs.fetchall()
	users = []
	for u in c:
		users.append(u)

	if search.validate_on_submit():
		return redirect('/search/%s' % search.keyword.data)

	return render_template("results.html",
		lists=lists,
		items=items,
		users=users,
		search=search,
		curruser=current_user)

if __name__ == '__main__':
   	app.run()