from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, abort
from flask_mysqldb import MySQL
import logging

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] =True #automatically reload templates on changes
app.config['SECRET_KEY'] = 'python'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'movie'

mysql = MySQL(app)

@app.route('/')
def website():
    return render_template('login.html')

    
@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == 'POST':
        email = request.form["email"]
        password = request.form["password"]
     
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = cur.fetchone()
    
        if user:
            # session['email'] = email
            return redirect(url_for("home"))
        else:
            flash('LOGIN FAILED!! PASSWORD OR EMAIL INCORRECT!', 'danger')
            return render_template('login.html')
        
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have successfully logged out', 'success')
    print('loggging off!!!')
    return render_template('login.html')


    
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        name = request.form["name"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
    
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return render_template('registration.html')
         
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        email_exists = cur.fetchone()
         
        if email_exists:
            flash('email already exist!', 'danger')
            return render_template("registration.html")
    
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (email, name, password, confirm_password) VALUES (%s, %s, %s, %s)", (email, name, password, confirm_password))
        mysql.connection.commit()
        cur.close()
        flash('Registration Successful!!', 'success')
        return render_template('login.html')
    
    return render_template('registration.html')


@app.route('/about')
def about():
    return render_template('about.html')

    
@app.route("/home")
def home():
    flash('LOGIN SUCCESSFUL! Welcome back!', 'success')
    return  render_template("home.html")
    
    
@app.route('/romance', methods=['GET', 'POST'])
def romance():
    
    return render_template('romance.html')
    
@app.route('/search-movies')
def search():
    query = request.method['query']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM movies WHERE title LIKE %s", ('%' + query + '%',))
    movies = cur.fetchall()
    return render_template('search_results.html', movies=movies)
    
    
    
if __name__ == '__main__':
    app.run(debug=True)