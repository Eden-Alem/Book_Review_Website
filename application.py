import os

from flask import Flask, session, render_template, redirect, flash, url_for, request, jsonify
from flask_session import Session
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash

from wtform_fields import *

import psycopg2
import urllib.parse as urlparse

app = Flask(__name__)

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

    
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


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    reg_form = RegistrationForm()

    if reg_form.validate_on_submit():
        username = reg_form.username.data
        email = reg_form.email.data
        password = reg_form.password.data

        with engine.connect() as connection:
            result_username = connection.execute(text(f"SELECT username FROM users WHERE username = '{username}' "))
            result_email = connection.execute(text(f"SELECT email FROM users WHERE email = '{email}' "))
            rows_username = result_username.fetchall()
            rows_email = result_email.fetchall()
            if len(rows_username) != 0 or len(rows_email) != 0:
                return 'Someone else has taken this username!'

        with engine.connect() as con:
            pword = generate_password_hash(password)
            con.execute(text(f"INSERT INTO Users(username,email , password) VALUES ('{username}','{email}','{pword}')"))

        session['username'] = username
        return redirect(url_for('index'))

    return render_template("signin.html", form=reg_form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    login_form = LoginForm()

    if login_form.validate_on_submit():
        username = login_form.username.data
        password = login_form.password.data


        with engine.connect() as connection:
            result = connection.execute(text(f"SELECT * FROM users WHERE username = '{username}'"))
            rows = result.fetchall()
            if len(rows) == 0:
                return 'Incorrect username.'
            elif not check_password_hash(rows[0]['password'], password):
                return 'Incorrect password.'
            else:
                user = rows[0]

        session['username'] = user['username']
        return redirect(url_for('index'))        

    return render_template("login.html", form=login_form)


@app.route('/logout')
def logout():
    if 'username' in session:
        session.pop('username')
    return render_template("home.html")


@app.route("/home", methods=['GET', 'POST'])
def index():
    if 'username' in session:
        username = session['username']
        search = Search()
        search_input = search.search_input.data
        
        searchquery = [] 

        if search.validate_on_submit():
            cur.execute("SELECT * FROM books WHERE title ~ (%s) OR author ~ (%s) OR isbn ~ (%s)", [search_input, search_input, search_input])
            dbRow = cur.fetchall()
            searchquery.append(dbRow)

            cur.close

        return render_template("index.html", form=search, searchquery=searchquery, username=username)
        

    return redirect(url_for('login')) 
    

@app.route("/edit", methods=['GET', 'POST'])
def edit():
    if 'username' in session:
        username = session['username']

        edit = Edit()

        selected_book = request.args.get('type')
        with engine.connect() as con:
            res = con.execute(text(f"SELECT review FROM Reviews WHERE isbn = '{selected_book}' AND username = '{username}'")).fetchall()
        response_placeholder = str(res[0][0])


        edit_input = edit.response.data
        
        session['isbn'] = selected_book
        if selected_book:
            with engine.connect() as connection:
                result = connection.execute(text(f"SELECT * FROM books WHERE isbn = '{selected_book}'"))
                rows = result.fetchall()
                session['value'] = rows[0]      
        
        if edit.validate_on_submit():
            with engine.connect() as con:
                con.execute(text(f"UPDATE Reviews SET review = '{edit_input}' WHERE isbn = '{selected_book}' AND username = '{username}'"))
            return redirect(url_for('details', type=session['isbn']))
        

        return render_template("edit.html", form=edit, username=username, value=session['value'], isbn=session['isbn'], response_placeholder=response_placeholder)
        
    return redirect(url_for('login'))



@app.route("/delete", methods=['GET', 'POST'])
def delete():
    if 'username' in session:
        username = session['username']

        selected_book = request.args.get('type')        

        session['isbn'] = selected_book
        if selected_book:
            with engine.connect() as connection:
                result = connection.execute(text(f"SELECT * FROM books WHERE isbn = '{selected_book}'"))
                rows = result.fetchall()
                session['value'] = rows[0]   

        with engine.connect() as con:
            con.execute(text(f"DELETE FROM Reviews WHERE isbn = '{selected_book}' AND username = '{username}'"))
        return redirect(url_for('details', type=session['isbn']))

    return redirect(url_for('login'))


@app.route("/details", methods=['GET', 'POST'])
def details():
    if 'username' in session:
        username = session['username']

        review = Review()
        message_input = review.review.data
        rate_input = review.rate.data

        listOfReviews = [] 

        selected_book = request.args.get('type')

        with engine.connect() as connection:
            result = connection.execute(text(f"SELECT * FROM reviews WHERE isbn = '{selected_book}' AND username = '{username}'")).fetchall()
           
            if len(result) == 0:
                if selected_book:
                    session['isbn'] = selected_book
                    with engine.connect() as connection:
                        result = connection.execute(text(f"SELECT * FROM books WHERE isbn = '{selected_book}'"))
                        rows = result.fetchall()
                        session['value'] = rows[0]      
                
                if review.validate_on_submit():
                    with engine.connect() as con:
                        con.execute(text(f"INSERT INTO Reviews(isbn, username, rating, review) VALUES ('{session['isbn']}','{username}','{rate_input}','{message_input}')"))
                
        cur.execute("SELECT * FROM reviews WHERE isbn = (%s)", [selected_book])
        dbRow = cur.fetchall()
        listOfReviews.append(dbRow)

        cur.close  

        elements = []
        if len(listOfReviews) != 0:
            for rev in listOfReviews[0]:
                if (rev[1] == username):
                    elements.append(rev)
                    listOfReviews[0].remove(rev)    

        return render_template("details.html", form=review, username=username, value=session['value'], listOfReviews=listOfReviews, elements=elements, isbn=session['isbn'])

    return redirect(url_for('login'))


@app.errorhandler(404)
def page_not_loading():
    return render_template('404.html'), 404


@app.route("/api/<string:isbn>", methods=['GET'])
def api(isbn):  
    rows_book = []
    error = None
    title = None
    author = None
    year = None
    review_count = None
    average_score = None
    with engine.connect() as connection:
        result = connection.execute(text(f"SELECT * FROM books WHERE isbn LIKE '{isbn}'"))
        rows_book = result.fetchall()
        if len(rows_book) == 0:
            return render_template("404.html")
        
        title=rows_book[0][1]
        author=rows_book[0][2]
        year=rows_book[0][3]
        with engine.connect() as connection:
            result = connection.execute(text(f"SELECT COUNT(isbn), AVG(rating) FROM reviews WHERE isbn='{isbn}'"))
            rows = result.fetchone()
            if rows is not None and len(rows) > 0:
                review_count = rows[0]
                average_score = rows[1]
    return jsonify(title=title,author=author,year=year,isbn=isbn,review_count=review_count,average_score=average_score)



