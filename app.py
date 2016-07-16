from flask import Flask, flash, session, render_template, request, json, redirect, url_for
import MySQLdb as db
import MySQLdb.cursors
import datetime
from wtforms import Form, BooleanField, StringField, PasswordField, validators
import hashlib, uuid, json

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
subsaiddits = None

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

class CommentForm(Form):
    text = StringField('Text', [validators.Length(min=4)])

################################################
#Requests and Routing
################################################

#Before Request Logic
@app.before_request
def before_request():
    global loggedIn
    loggedIn = 'user' in session
    global subsaiddits
    subsaiddits = get_subsaiddits()

#Globals injection
@app.context_processor
def inject_globals():
    globalsDict = {
        'subsaiddits': subsaiddits,
        'loggedIn' : loggedIn
    }
    return globalsDict

#Index Page
@app.route("/")
def index():
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
                flash(u'Account Created', 'success')
                return redirect(url_for('login'))
            else:
                flash(u'Registeration failed', 'error')
        else:
            flash(u'Passwords must match', 'error')
    return render_template('register.html', form=form)

#Subsaiddit creation
@app.route("/create", methods=['GET', 'POST'])
def create_subsaiddit():
    if not loggedIn:
        flash(u'You must be logged in to create a new subsaiddit', 'error')
        return redirect(url_for('login'))

    form = SubsaidditForm(request.form)
    #If post then handle input
    if request.method == 'POST' and form.validate():
        title = form.title.data
        description = form.description.data
        is_default = form.is_default.data
        if new_subsaiddit(title, description, is_default):
            flash(u'Subsaiddit Created', 'success')
            return redirect(url_for('create_subsaiddit'))
        else:
            flash(u'Subsaiddit Creation failed', 'error')
    return render_template('create_subsaiddit.html', form=form)

#View and post to subsaiddit
@app.route('/s/<subsaiddit_title>', methods=['GET', 'POST'])
def view_subsaiddit(subsaiddit_title):
    subsaiddit = get_subsaiddit(subsaiddit_title)
    is_subscribed = get_is_subscribed(subsaiddit['id'])
    if (subsaiddit == None):
        flash(u'Subsaiddit ' + subsaiddit_title + ' does not exist', 'error')
        return redirect(url_for('index'))

    form = PostForm(request.form)
    if request.method == 'POST' and form.validate():
        if not loggedIn:
            flash(u'You must be logged in to create a new post', 'error')
            return redirect(url_for('login'))
        title = form.title.data
        text = form.text.data
        if new_post(subsaiddit['id'], title, text):
            flash(u'Post Created', 'success')

    posts = get_posts([str(subsaiddit['id'])])
    return render_template('subsaiddit.html', subsaiddit=subsaiddit, posts=posts, form=form, is_subscribed=is_subscribed)

#View an account and add friends
@app.route('/a/<username>', methods=['GET', 'POST'])
def view_account(username):
    user = get_user(username)
    is_friend = get_is_friend(user['id'])
    if (user == None):
        flash(u'User ' + usersername + ' does not exist', 'error')
        return redirect(url_for('index'))

    posts = get_user_posts([str(user['id'])])
    return render_template('user.html', user=user, posts=posts, form=form, is_friend=is_friend)


#Vote on post or comment
@app.route('/vote', methods=['POST'])
def vote():
    if not loggedIn:
        return json.dumps({'success':False, 'message':"You must be logged in to vote"})
    success = vote(request.json['updown'], request.json['postid'], request.json['commentid'])
    if success:
        return json.dumps({'success':True})
    else:
        return json.dumps({'success':False, 'message':"Failed to submit vote. Make sure you aren't voting a second time on the same post/comment."})

#View post
@app.route('/s/<subsaiddit_title>/<post_id>', methods=['GET'])
def post(subsaiddit_title, post_id):
    post = get_post(post_id);
    comments = get_comments(post_id);
    return render_template('view_post.html', post=post, comments=comments, subsaiddit_title=subsaiddit_title)

#Comment creation
@app.route("/comment/<subsaiddit_title>/<post_id>/<comment_id>", methods=['GET', 'POST'])
def comment(subsaiddit_title, post_id, comment_id):
    if not loggedIn:
        flash(u'You must be logged in to comment', 'error')
        return redirect(url_for('login'))

    form = CommentForm(request.form)
    #If post then handle input
    if request.method == 'POST' and form.validate():
        text = form.text.data

        #Instead of using a null commentid for a vote on a post and not a comment,
        #use -1, so we can keep the unique property on votes on posts
        if comment_id == 'NULL':
            comment_id = -1

        if new_comment(text, post_id, comment_id):
            flash(u'Comment Created', 'success')
            return redirect(url_for('post', subsaiddit_title=subsaiddit_title, post_id=post_id))

        else:
            flash(u'Comment Creation failed', 'error')
    return render_template('comment.html', form=form, subsaiddit_title=subsaiddit_title, post_id=post_id, comment_id=comment_id)

#Delete post
@app.route('/deletepost', methods=['POST'])
def delete_post():
    success = delete_post(request.json['postid'])
    if success:
        return "Post Deleted"
    else:
        return "Failed to Delete post. Make sure you are the creator of this post", 401

#Subscribe or Unsubscrive
@app.route('/changesubscription', methods=['POST'])
def change_subscription():
    if change_subscription(request.json['subscribe'], request.json['subsaiddit_id']):
        flash(u'Subscription update successful', 'success')
    else:
        flash(u'Subscription update failed', 'error')
    return ""

#Friendship creation
@app.route("/createfriendship/<friend_id>", methods=['GET', 'POST'])
def create_friendship(friend_id):
    print request.headers['Referer']

    if create_friendship(friend_id):
        flash(u'Friendship Created', 'success')
        return redirect(request.headers['Referer'])
    else:
        flash(u'Friendship Creation Failed', 'error')
    return redirect(request.headers['Referer'])


#Favourite post
@app.route('/favouritepost', methods=['POST'])
def favourite_post():
    success = favourite_post(request.json['postid'])
    if success:
        return "Post Favourited"
    else:
        return "Failed to favourite post. Maybe you've already favourited it?", 500

################################################
#Model functions
################################################

#Register User
def register_user(username, password):
    username = conn.escape(username)
    #Check to see if username is in use
    cursor.execute("SELECT COUNT(id) FROM accounts WHERE username = %s", [username])
    count = cursor.fetchone()
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

#Get a user
def get_user(username):
    username = conn.escape(username)
    cursor.execute("SELECT * FROM accounts WHERE username = %s", [username])
    user = cursor.fetchone()
    #If user does not exist return false
    if not user:
        return False
    else:
        return user

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

def get_is_subscribed(subsaiddit_id):
    if 'user' not in session:
        return False

    account_id = session['user']['id']
    cursor.execute("SELECT * FROM subscribes WHERE account_id = %s AND subsaiddit_id = %s", [account_id, subsaiddit_id])
    subsaiddit = cursor.fetchone()
    if subsaiddit:
        return True
    else:
        return False

def get_posts(subsaiddits, page=1):
    id_list = ','.join(subsaiddits)
    cursor.execute("SELECT * FROM posts JOIN accounts ON posts.created_by = accounts.id JOIN subsaiddits on posts.subsaiddit = subsaiddits.id WHERE posts.subsaiddit IN (%s) LIMIT 20", [id_list])
    return cursor.fetchall()

def get_user_posts(users, page=1):
    id_list = ','.join(users)
    cursor.execute("SELECT * FROM posts JOIN accounts ON posts.created_by = accounts.id JOIN subsaiddits on posts.subsaiddit = subsaiddits.id WHERE posts.created_by IN (%s) LIMIT 20", [id_list])
    return cursor.fetchall()

def vote(up_down, post_id, comment_id):
    if 'user' not in session:
        return False

    account_id = session['user']['id']
    up_down = conn.escape(up_down)
    post_id = conn.escape(post_id)
    comment_id = conn.escape(comment_id)

    try:
        cursor.execute("REPLACE INTO votes (up_down, account_id, post_id, comment_id) VALUES(%s,%s,%s,%s)", [up_down, account_id, post_id, comment_id])
        conn.commit()
    except Exception:
        return False
    return True

def new_comment(text, post_id, comment_id):
    if 'user' not in session:
        return False
    text_content = conn.escape(text)
    created = str(datetime.datetime.now())
    created_by = session['user']['id']

    if comment_id == 'NULL':
        cursor.execute("INSERT INTO Comments (text_content, created, post, reply_to, created_by) VALUES(%s,%s,%s,NULL,%s)", [text_content, created, post_id, created_by])
    else:
        cursor.execute("INSERT INTO Comments (text_content, created, post, reply_to, created_by) VALUES(%s,%s,%s,%s,%s)", [text_content, created, post_id, comment_id, created_by])
    conn.commit()
    return True

def get_post(post_id):
    cursor.execute("SELECT * FROM Posts JOIN accounts ON posts.created_by = accounts.id JOIN subsaiddits on posts.subsaiddit = subsaiddits.id WHERE posts.id = %s", [post_id])
    post = cursor.fetchone()
    return post

def get_comments(post_id, reply_to=-1):
    cursor.execute("SELECT * FROM Comments JOIN accounts ON comments.created_by = accounts.id WHERE comments.post = %s AND comments.reply_to = %s", [post_id, reply_to])
    comments = cursor.fetchall()
    return comments

def get_votes(post_id, comment_id=0, useAccount=False):
    if useAccount:
        if loggedIn:
            account_id = session['user']['id']
        else:
            return False
        cursor.execute("SELECT up_down, COUNT(account_id) AS num FROM Votes WHERE post_id = %s AND comment_id = %s AND account_id = %s GROUP BY up_down", [post_id, comment_id, account_id])
        votes = cursor.fetchone()
    else:
        cursor.execute("SELECT up_down, COUNT(account_id) AS num FROM Votes WHERE post_id = %s AND comment_id = %s GROUP BY up_down", [post_id, comment_id])
        votes = cursor.fetchall()
    print votes
    return votes

def delete_post(post_id):
    if 'user' not in session:
        return False
    cursor.execute("SELECT * FROM Posts WHERE id = %s", [post_id])
    post = cursor.fetchone()

    if post['created_by'] != session['user']['id']:
        return False

    try:
        cursor.execute("DELETE FROM Posts WHERE id = %s", [post_id])
        conn.commit()
    except Exception:
        return False
    return True

def change_subscription(change_subscription, subsaiddit_id):
    if 'user' not in session:
        return False
    account_id = session['user']['id']
    subsaiddit_id = subsaiddit_id
    if change_subscription:
        cursor.execute("INSERT INTO Subscribes (account_id, subsaiddit_id) VALUES(%s,%s)", [account_id, subsaiddit_id])
    else:
        cursor.execute("DELETE FROM Subscribes WHERE account_id = %s AND subsaiddit_id = %s", [account_id, subsaiddit_id])
    conn.commit()
    return True

def get_is_friend(friend_id):
    if 'user' not in session:
        return False
    cursor.execute("SELECT * FROM Friends WHERE (account_1_id = %s AND account_2_id = %s) OR (account_2_id = %s AND account_1_id = %s)", [session['user']['id'],friend_id,session['user']['id'],friend_id])
    is_friend = cursor.fetchone()
    if is_friend:
        return True
    else:
        return False

def create_friendship(friend_id):
    if 'user' not in session:
        return False

    if get_is_friend(friend_id):
        flash(u'You are alread friends with this user', 'error')
        return False

    cursor.execute("INSERT INTO Friends (account_1_id, account_2_id) VALUES(%s,%s)", [session['user']['id'], friend_id])
    conn.commit()
    return True


def favourite_post(post_id):
    if 'user' not in session:
        return False
    account_id = session['user']['id']
    try:
        cursor.execute("INSERT INTO Favourites (account_id, post_id) VALUES(%s,%s)", [account_id, post_id])
        conn.commit()
    except Exception:
        return False
    return True


################################################
#Helper functions
################################################
app.add_template_global(get_comments, name='get_comments')
app.add_template_global(get_votes, name='get_votes')

################################################
#Main
################################################
if __name__ == "__main__":
    app.run(debug=True)
