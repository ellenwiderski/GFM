import psycopg2

conn = psycopg2.connect(database="xmasapp")

curs = conn.cursor() 

curs.execute('''drop table IF EXISTS users CASCADE''')
curs.execute('''CREATE TABLE users (
	user_name text PRIMARY KEY,
	password text, 
	display_name text, 
	naughty boolean);''')

curs.execute('''INSERT INTO users values ('MickeyMouse', 'passwordplease', 'Mickey', '1');''')


curs.execute('''DROP TABLE IF EXISTS item CASCADE''')
curs.execute('''CREATE TABLE item (
	item_name text primary key, 
	item_price int, 
	item_link text);''')

curs.execute('''INSERT INTO item values ('adventure pack', 50, 'www.patagonia.com');''')

curs.execute('''drop table IF EXISTS list CASCADE''')
curs.execute('''CREATE TABLE list (list_id serial primary key, list_name text, user_name text references users(user_name));''')

curs.execute('''INSERT INTO list values (1,'Christmas List', 'MickeyMouse');''')


curs.execute('''drop table IF EXISTS list_item CASCADE''')
curs.execute('''CREATE TABLE list_item (item_name text references item(item_name), list_id int references list(list_id));''')

curs.execute('''INSERT INTO list_item values ('adventure pack', 1);''')

conn.commit() #make this change permanent