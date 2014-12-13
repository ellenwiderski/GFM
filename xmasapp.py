import sqlite3


conn = sqlite3.connect("xmasapp.db") #create a connection (most databases are a client-server relationship, where requests are being sent and received

curs = conn.cursor() #cursor is the position or what row we are on in the db - a pointer to where we are in the db

curs.execute('''drop table user''')
curs.execute('''Create table user (user_name text primary key, password text, display_name text, naughty boolean);''')

curs.execute('''insert into user values ('MickeyMouse', 'passwordplease', 'Mickey', 1)''')


curs.execute('''drop table item''')
curs.execute('''Create table item (item_name text primary key, item_price int, item_link text);''')

curs.execute('''insert into item values ('adventure pack', 50, 'www.patagonia.com')''')


curs.execute('''drop table list''')
curs.execute('''Create table list (list_id integer primary key autoincrement, list_name text, user_name text, foreign key(user_name) references user(user_name));''')

curs.execute('''insert into list values (1,'Christmas List', 'MickeyMouse')''')


curs.execute('''drop table list_item''')
curs.execute('''Create table list_item (item_name text, list_id int, foreign key(item_name) references item(item_name), foreign key(list_id) references list(list_id));''')

curs.execute('''insert into list_item values ('adventure pack', 1)''')

conn.commit() #make this change permanent