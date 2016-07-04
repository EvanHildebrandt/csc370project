from flask import Flask, session, render_template, request, json, redirect, url_for
import MySQLdb as db
import MySQLdb.cursors
from wtforms import Form, BooleanField, StringField, PasswordField, validators
import hashlib, uuid
app = Flask(__name__)

#Secret key for sessions
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

#Connect to database
conn = MySQLdb.connect(
    host = 'localhost',
    user = '',
    passwd = '',
    db = 'saiddit',
    cursorclass=MySQLdb.cursors.DictCursor
)
cursor = conn.cursor()

#Form creation and validation
class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')

class LoginForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('Password')

#Global Variables
loggedIn = False

#Before Request Logic
@app.before_request
def before_request():
    global loggedIn
    loggedIn = 'user' in session

#Index Page
@app.route("/")
def index():
	cursor.execute("show databases")
	tables = cursor.fetchall()
	return render_template(
		'index.html',
		 tables=tables,
		 loggedIn=loggedIn
	)

#Login Page + Form Handling
@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    #If post then handle input
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data
        #Attempt to login user
        if login_user(username, password):
            return redirect(url_for('index'))
    return render_template('login.html', form=form)

#Logout Route
@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

#Register Page + Form Handling
@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    #If post then handle input
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password_1 = form.password.data
        password_2 = form.confirm.data
        #Passwords Must Match
        if (password_1 == password_2):
            #Attempt to register user
            if register_user(username, password_1):
                return redirect(url_for('login'))
    return render_template('register.html', form=form)

#Register User
def register_user(username, password):
    username = conn.escape(username)
    #Check to see if username is in use
    cursor.execute("SELECT COUNT(id) FROM accounts WHERE username = %s", [username])
    count = cursor.fetchone()
    print count[0]
    if (count[0] > 0):
        print "user exists"
        return False
    else:
        #Create salt and hash password
        salt = uuid.uuid4().hex
        hashed_password = hashlib.sha512(password + salt).hexdigest()
        #Insert new user
        cursor.execute("INSERT INTO accounts (username, password, salt) VALUES(%s, %s, %s)", [username, hashed_password, salt])
        conn.commit()
        return True

#Login User
def login_user(username, password):
    username = conn.escape(username)
    #Fetch User By Username
    cursor.execute("SELECT * FROM accounts WHERE username = %s", [username])
    user = cursor.fetchone()
    #If user does not exist return false
    if not user:
        return False
    #Create hashstring with entered password and stored salt
    hashed_password = hashlib.sha512(password + user['salt']).hexdigest()
    #Check if hashed password matches stored password
    if hashed_password == user['password']:
        #Set session Variable to store user
        session['user'] = user
        return True
    else:
        return False


if __name__ == "__main__":
	app.run(debug=True)
