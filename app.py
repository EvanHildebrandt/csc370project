from flask import Flask, flash, session, render_template, request, json, redirect, url_for
import MySQLdb as db
import MySQLdb.cursors
import datetime
from wtforms import Form, BooleanField, StringField, PasswordField, validators
import hashlib, uuid

################################################
#App initilization
################################################

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

#Global Variables
loggedIn = False

################################################
#Form creation and validation
################################################

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

class SubsaidditForm(Form):
    title = StringField('Title', [validators.Length(min=4, max=25)])
    is_default = BooleanField('Is Default?')
    description = StringField('Description', [validators.Length(min=4, max=25)])

class PostForm(Form):
    title = StringField('Title', [validators.Length(min=4, max=25)])
    text = StringField('Text', [validators.Length(min=4)])


################################################
#Requests and Routing
################################################

#Before Request Logic
@app.before_request
def before_request():
    global loggedIn
    loggedIn = 'user' in session

#Index Page
@app.route("/")
def index():
    subsaiddits = get_subsaiddits()
    id_list = []
    for subsaiddit in subsaiddits:
        id_list.append(str(subsaiddit['id']))
    posts = get_posts(id_list)

    return render_template(
        'index.html',
         subsaiddits=subsaiddits,
         posts=posts,
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
            flash(u'Logged In', 'success')
            return redirect(url_for('index'))
        else:
            flash(u'Incorrect username or password', 'error')
    return render_template('login.html', form=form)

#Logout Route
@app.route("/logout")
def logout():
    session.pop('user', None)
    flash(u'Logged Out', 'success')
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
            else:
                flash(u'Registeration failed', 'error')
        else:
            flash(u'Passwords must match', 'error')
    return render_template('register.html', form=form)

#Register Page + Form Handling
@app.route("/create", methods=['GET', 'POST'])
def create_subsaiddit():
    form = SubsaidditForm(request.form)
    #If post then handle input
    if request.method == 'POST' and form.validate():
        title = form.title.data
        description = form.description.data
        is_default = form.is_default.data
        if new_subsaiddit(title, description, is_default):
            flash(u'Subsaiddit Created failed', 'error')
            return redirect(url_for('create_subsaiddit'))
        else:
            flash(u'Subsaiddit Creation failed', 'error')
    return render_template('create_subsaiddit.html', form=form)

#View and post to subsaiddit
@app.route('/s/<subsaiddit_title>', methods=['GET', 'POST'])
def view_subsaiddit(subsaiddit_title):
    subsaiddit = get_subsaiddit(subsaiddit_title)
    if (subsaiddit == None):
        flash(u'Subsaiddit ' + subsaiddit_title + ' does not exist', 'error')
        return redirect(url_for('index'))

    form = PostForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        text = form.text.data
        if new_post(subsaiddit['id'], title, text):
            flash(u'Post Created', 'success')

    posts = get_posts([str(subsaiddit['id'])])
    return render_template('subsaiddit.html', subsaiddit=subsaiddit, posts=posts, form=form)


################################################
#Model functions
################################################

#Register User
def register_user(username, password):
    username = conn.escape(username)
    #Check to see if username is in use
    cursor.execute("SELECT COUNT(id) FROM accounts WHERE username = %s", [username])
    count = cursor.fetchone()
    print count
    if (count['COUNT(id)'] > 0):
        flash(u'That username is already in use', 'error')
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

def new_subsaiddit(title, description, is_default):
    title = conn.escape(title)
    description = conn.escape(description)
    is_default = is_default
    created = str(datetime.datetime.now())
    created_by = str(session['user']['id'])
    cursor.execute("SELECT COUNT(id) FROM subsaiddits WHERE subsaiddit_title = %s", [title])
    count = cursor.fetchone()
    if (count['COUNT(id)'] > 0):
        return False
    else:
        #Insert new subsaiddit
        cursor.execute("INSERT INTO subsaiddits (subsaiddit_title, description, is_default, created, created_by) VALUES(%s, %s, %s, %s, %s)", [title, description, is_default, created, created_by])
        conn.commit()
        return True

def new_post(subsaiddit_id, title, text):
    title = conn.escape(title)
    text = conn.escape(text)
    created = str(datetime.datetime.now())
    created_by = session['user']['id']
    subsaiddit = str(subsaiddit_id)
    cursor.execute("INSERT INTO posts (title, text_content, created, created_by, subsaiddit) VALUES(%s,%s,%s,%s,%s)", [title, text, created, created_by, subsaiddit])
    conn.commit()
    return True

#Get list of subsaiddits
def get_subsaiddits():
    if 'user' in session:
        cursor.execute('''SELECT * FROM subscribes JOIN subsaiddits ON subscribes.subsaiddit_id = subsaiddits.id WHERE subscribes.account_id = %s''', [str(session['user']['id'])])
    else:
        cursor.execute('''SELECT * FROM subsaiddits WHERE subsaiddits.is_default = TRUE''')
    subsaiddits = cursor.fetchall()
    return subsaiddits

def get_subsaiddit(subsaiddit_title):
    cursor.execute("SELECT * FROM subsaiddits WHERE subsaiddits.subsaiddit_title = %s", [subsaiddit_title])
    subsaiddit = cursor.fetchone()
    return subsaiddit

def get_posts(subsaiddits, page=1):
    id_list = ','.join(subsaiddits)
    cursor.execute("SELECT * FROM posts WHERE posts.subsaiddit IN (%s) LIMIT 20", [id_list])
    return cursor.fetchall()

################################################
#Helper functions
################################################


################################################
#Main
################################################
if __name__ == "__main__":
	app.run(debug=True)
