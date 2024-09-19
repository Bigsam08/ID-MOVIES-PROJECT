from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, abort, make_response
from flask_mysqldb import MySQL
from flask_login import current_user, logout_user, LoginManager, login_user, login_required, UserMixin

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] =True #automatically reload templates on changes
app.config['SECRET_KEY'] = 'python'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'movie'

mysql = MySQL(app)

login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, email):
        self.email = email
        
    def get_id(self):
        return self.email #returns the email as the user id
        

@login_manager.user_loader
def load_user(email):
    return User(email)


from flask_login import current_user

def get_current_user_email():
    if current_user.is_authenticated:
        return current_user.email  # Assuming 'email' is an attribute of the User model
    return None




@app.route('/')
def website():
    return render_template('login.html')

@app.errorhandler(401)
def unauthorized(error):
    return redirect(url_for('login'))  # Redirect to login page


    
@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == 'POST':
        email = request.form["email"]
        password = request.form["password"]
     
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = cur.fetchone()
    
        if user:
            user = User(email)
            login_user(user)
            return redirect(url_for("home"))
        else:
            flash('LOGIN FAILED!! PASSWORD OR EMAIL INCORRECT!', 'danger')
            return render_template('login.html')
        
    return render_template('login.html')


@app.route('/logout', methods=["POST"])
@login_required
def logout():
    logout_user()
    session.clear()
    flash('You have successfully logged out', 'success')
    return redirect( url_for('login'))


    
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
@login_required
def home():
    flash('LOGIN SUCCESSFUL! Welcome back!', 'success')
    return  render_template("home.html")
    
    
@app.route('/romance', methods=['GET', 'POST'])
@login_required
def romance():
    try:
        user_email = get_current_user_email()  # Retrieve the current user's email

        if request.method == "POST":
            data = request.get_json()
            vote_id = data.get('vote')

            # Ensure the cursor is defined
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM user_votes WHERE email = %s", (user_email,))
            existing_vote = cur.fetchone()

            if existing_vote:
                return jsonify({'error': 'You have already voted.'}), 403

            # Record the vote
            cur.execute("UPDATE r_movies SET votes = votes + 1 WHERE id = %s", (vote_id,))
            cur.execute("INSERT INTO user_votes (email, movie_id) VALUES (%s, %s)", (user_email, vote_id))
            mysql.connection.commit()

            percentages = get_vote_percentages()
            return jsonify(percentages)

        # For GET requests
        cur = mysql.connection.cursor()
        percentages = get_vote_percentages()
        cur.execute("SELECT * FROM user_votes WHERE email = %s", (user_email,))
        has_voted = cur.fetchone() is not None
        
        return render_template('romance.html', percentages=percentages, has_voted=has_voted)

    except Exception as e:
        return jsonify({'error': str(e)}), 500



def get_vote_percentages():
    cur = mysql.connection.cursor()
    cur.execute("SELECT title, votes FROM r_movies")
    results = cur.fetchall()
    
    total_votes = sum([votes for title, votes in results])
    percentages = {title: (votes / total_votes) * 100 if total_votes > 0 else 0 for title, votes in results}
    
    return {
        'WithUs': round(percentages.get('WithUs', 0), 2),
        'Moon': round(percentages.get('Moon', 0), 2),
        'Lagrimas': round(percentages.get('Lagrimas', 0), 2)
    }

    
    
    
@app.route('/search-movies')
def search():
    query = request.method['query']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM movies WHERE title LIKE %s", ('%' + query + '%',))
    movies = cur.fetchall()
    return render_template('search_results.html', movies=movies)
    
    
    
if __name__ == '__main__':
    app.run(debug=True)