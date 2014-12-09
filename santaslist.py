from flask import Flask, request, render_template, redirect, flash
from flask.ext.wtf import Form
from wtforms import TextField, PasswordField
from wtforms.validators import InputRequired
import sqlite3

app = Flask(__name__)
app.debug = True   # need this for autoreload and stack trace
app.config.from_object('config')

conn = sqlite3.connect("xmasapp.db") #create a connection (most databases are a client-server relationship, where requests are being sent and received
curs = conn.cursor() #cursor is the position or what row we are on in the db - a pointer to where we are in the db
# curs.execute('''Create table user (user_name text primary key, password text, display_name text, age int, naughty boolean);''')
# curs.execute('''Create table item (item_name text primary key, item_price int, item_link text);''')
# curs.execute('''Create table list (list_id int primary key, user_name text, foreign key(user_name) references user(user_id));''')
# curs.execute('''Create table list_item (list_item_id int primary key, item_name text, list_id int, foreign key(item_name) references item(item_name), foreign key(list_id) references list(list_id));''')


# curs.execute('''insert into list values (1, 'MickeyMouse')''')
# curs.execute('''insert into item values ('adventure pack', 50, 'www.patagonia.com')''')
# curs.execute('''insert into user values ('MickeyMouse', 'passwordplease', 'Mickey', 12, 1)''')
# curs.execute('''insert into list_item values (1, 'adventure pack', 1)''')
# conn.commit() #make this change permanent

class LoginForm(Form):
	username = TextField('Username',validators=[InputRequired()])
	password = PasswordField('Password',validators=[InputRequired()])

@app.route('/', methods=['GET','POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		username = form.username.data
		password = form.password.data
		user = curs.execute('''SELECT user_name FROM user WHERE user_name = '%s' and password = '%s';'''% (username,password))
		if user is None:
			return render_template('login.html')
		else:
			return redirect('/user/%s' % username)

	return render_template('login.html',form=form)

@app.route('/user/<username>', methods=['GET','POST'])
def profile(username):
	listdict = {}
	lists = curs.execute('''SELECT list.list_id FROM user, list WHERE list.user_name = user.user_name;''')
	for list in lists:
		items = curs.execute('''SELECT item.item_name, item.item_price, item.item_link from item, list, list_item WHERE list_item.list_item_id = list.list_id and list.list_id = '%s';'''%list[0])
		listdict[list[0]] = items
	return render_template('profile.html',listdict=listdict)

@app.route('/signup',methods=['GET','POST'])
def signup():
	form = LoginForm()
	# if form.validate_on_submit():
	# 	username = form.username.data
	# 	password = form.password.data
	# 	user = curs.execute('''SELECT user_name FROM user WHERE user_name = '%s';'''% username)
	# 	if user is None:
	# 		curs.execute('''INSERT INTO user values('%s','%s','poophead',13,1);'''%(username,password))
	# 		return redirect('/user/%s' % username)
	# 	else:
	# 		return render_template('signup.html',form=form)

	return render_template('signup.html',form=form)

if __name__ == '__main__':
   	app.run()