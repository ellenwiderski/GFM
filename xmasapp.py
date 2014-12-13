import psycopg2

conn = psycopg2.connect("dbname=d4gnik1781p8qs host=ec2-54-243-44-191.compute-1.amazonaws.com port=5432 user=ecxyptlvfvtqfi password=Iyi4Mc9aJEax2o_5tyIx1SKAGk sslmode=require")

curs = conn.cursor() 

curs.execute('''drop table IF EXISTS users CASCADE''')
curs.execute('''CREATE TABLE users (
	user_name text PRIMARY KEY,
	password text, 
	display_name text, 
	naughty boolean);''')

curs.execute('''DROP TABLE IF EXISTS item CASCADE''')
curs.execute('''CREATE TABLE item (
	item_name text primary key, 
	item_price int, 
	item_link text);''')

curs.execute('''drop table IF EXISTS list CASCADE''')
curs.execute('''CREATE TABLE list (
	list_id serial primary key, 
	list_name text, 
	user_name text references users(user_name));''')

curs.execute('''drop table IF EXISTS list_item CASCADE''')
curs.execute('''CREATE TABLE list_item (item_name text references item(item_name), list_id int references list(list_id));''')

conn.commit()