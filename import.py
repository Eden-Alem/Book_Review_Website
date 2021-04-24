import psycopg2
import urllib.parse as urlparse
import os
import csv

url = urlparse.urlparse(os.environ['DATABASE_URL'])
dbname = url.path[1:]
user = url.username
password = url.password
host = url.hostname
port = url.port

con = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
            )

print("Connecting to Database")
cur = con.cursor()

cur.execute("""
DROP TABLE IF EXISTS Books;\n
CREATE TABLE Books(
    isbn TEXT,
    title TEXT,
    author TEXT,
    year INT,
    id SERIAL PRIMARY KEY
);
""")

cur.execute("""
DROP TABLE IF EXISTS Users;\n
CREATE TABLE users(
 id SERIAL PRIMARY KEY,
 email TEXT UNIQUE NOT NULL,
 username VARCHAR(25) UNIQUE NOT NULL,
 password TEXT NOT NULL
);
""")


cur.execute("""
DROP TABLE IF EXISTS Reviews;\n
CREATE TABLE Reviews(
    isbn TEXT, 
    username TEXT, 
    rating FLOAT, 
    review TEXT,
    id SERIAL PRIMARY KEY
);
""")

with open('books.csv', 'r') as f:
    print("reading data from csv file to insert to database")
    next(f)
    print("insertion started.")

    for i, l in  enumerate(csv.reader(f, quotechar='"', delimiter=',',
                     quoting=csv.QUOTE_ALL, skipinitialspace=True)):
        cur.execute("INSERT INTO Books (isbn, title, author, year) VALUES(%s, %s, %s, %s)", (l[0], l[1], l[2], int(l[3]))) 
        print(f"{i} of {5000} inserted")
    print("insertion completed")
con.commit()
con.close()