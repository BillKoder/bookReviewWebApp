from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from BookReviewDatabase import Base, User, Book, Forum, ForumContent, BookForumConnect
from flask import session as login_session
import random, string, datetime
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
# mail sending function
#import smtplib
# email modules
#from email.mime.text import MIMEText
from flask_mail import Mail, Message
#from app import mail

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']


app = Flask(__name__)

engine = create_engine('sqlite:///bookreview.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind = engine)
session = DBSession()

# Main page for Website, Shows all the book
@app.route('/')
@app.route('/books/')
def bookList():
	books = session.query(Book)
	if 'username' not in login_session:
  		return render_template('publicBookList.html', books = books)
  	else:
  		user = getUserInfo(login_session['user_id'])
		return render_template('bookList.html', books = books, user = user)

# Route for individual book information
@app.route('/books/<int:book_id>/')
def bookInformation(book_id):
	book = session.query(Book).filter_by(id = book_id).one()
	creator = getUserInfo(book.user_id)
	bookSearch = book.title
	print bookSearch
	bookSearch = bookSearch.replace(" ", "+")
	print bookSearch
	url = "http://www.amazon.com/s?index=books&field-title=" + bookSearch
	if 'username' in login_session:
		user = getUserInfo(login_session['user_id'])
		return render_template('bookinfo.html', book = book, creator = creator, url = url, user = user)
	else:
		return render_template('publicbookinfo.html', book = book, creator = creator, url = url)

# Route for adding a new book
@app.route('/books/new', methods = ['GET', 'POST'])
def newBook():
	if 'username' not in login_session:
		flash("You must be logged in to access that page.")
		return redirect('/login')
	user = getUserInfo(login_session['user_id'])
	if request.method == 'POST':
		newBook = Book(title = request.form['title'],
			author = request.form['author'],
			subject = request.form['subject'],
			summary = request.form['summary'],
			picture = request.form['picture'],
			user_id = login_session['user_id'])
		session.add(newBook)
		session.commit()
		flash("New book Created!")
		return redirect(url_for('bookList'))
	else:
		return render_template('newBook.html', user = user)



# Route for editing book information
@app.route('/books/<int:book_id>/edit', methods = ['GET', 'POST'])
def editBook(book_id):
	if 'username' not in login_session:
		flash("You must be logged in to access that page.")
		return redirect('/login')
	user = getUserInfo(login_session['user_id'])
	editBook = session.query(Book).filter_by(id = book_id).one()
	if login_session['user_id'] != editBook.user_id:
		flash("Only user who added this book can edit it.")
		return redirect(url_for('bookInformation', book_id = book_id))
	if request.method == 'POST':
		if request.form['title']:
			editBook.title = request.form['title']
		if request.form['author']:
			editBook.author = request.form['author']
		if request.form['subject']:
			editBook.subject = request.form['subject']
		if request.form['category']:
			editBook.category = request.form['category']
		if request.form['summary']:
			editBook.summary = request.form['summary']
		if request.form['picture']:
			editBook.picture = request.form['picture']
		session.add(editBook)
		session.commit()
		return redirect(url_for('bookInformation', book_id = book_id))
	else:
		return render_template('editBook.html', book_id = book_id, editBook = editBook, user = user)

# Route for deleting book information
@app.route('/books/<int:book_id>/delete', methods = ['GET', 'POST'])
def deleteBook(book_id):
	if 'username' not in login_session:
		flash("You must be logged in to access that page.")
		return redirect('/login')
	user = getUserInfo(login_session['user_id'])
	bookToDelete = session.query(Book).filter_by(id = book_id).one()
	if login_session['user_id'] != bookToDelete.user_id:
		flash("Only user who added this book can delete it.")
		return redirect(url_for('bookInformation', book_id = book_id))
	if request.method == 'POST':
		session.delete(bookToDelete)
		session.commit()
		return redirect(url_for('bookList'))
	else:
		return render_template('deleteBook.html', bookToDelete = bookToDelete, user = user)

# Route for login page
@app.route('/login')
def login():
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
	login_session['state'] = state
	return render_template('login.html', STATE = state,)

#Route for connecting through google account
@app.route('/gconnect', methods=['POST'])
def gconnect():
	if request.args.get('state') != login_session['state']:
		response = make_response(json.dumps('Invalid state parameter'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	code = request.data
	try:
		# Upgrade the authorization code into a credentials object
		oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
		oauth_flow.redirect_uri = 'postmessage'
		credentials = oauth_flow.step2_exchange(code)
	except FlowExchangeError:
		response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	# Check that the access token is valid
	access_token = credentials.access_token
	url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' %access_token)
	h = httplib2.Http()
	result = json.loads(h.request(url, 'GET')[1])
	# If there was an error in the access token info, abort
	if result.get('error') is not None:
		response = make_response(json.dumps(result.get('error')),500)
		response.headers['Content-Type'] = 'application/json'
	# Verify that the access token is used for the intended user
	gplus_id = credentials.id_token['sub']
	if result['user_id'] != gplus_id:
		response = make_response(json.dumps("Token's user ID doesn't match given user ID."), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	# Verify that the access token is valid for this app
	if result['issued_to'] != CLIENT_ID:
		response = make_response(json.dumps("Token's client ID does not match app's"), 401)
		print "Token's client ID doesn't match app's"
		response.headers['Content-Type'] = 'application/json'
		return response
	# Check to see if user is already logged in
	stored_access_token = login_session.get('access_token')
	stored_gplus_id = login_session.get('gplus_id')
	if stored_access_token is not None and gplus_id == stored_gplus_id:
		response = make_response(json.dumps('Current user is already connected.'), 200)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Store the access token in the seesion for later use.
	login_session['provider'] = 'google'
	login_session['access_token'] = credentials.access_token
	login_session['gplus_id'] = gplus_id

	# Get user info
	userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
	params = {'access_token': credentials.access_token, 'alt':'json'}
	answer = requests.get(userinfo_url, params=params)
	data = json.loads(answer.text)

	login_session['username'] = data["name"]
	login_session['picture'] = data["picture"]
	login_session['email'] = data["email"]

	# See if user exists in database, if it doesn't make a new one
	user_id = getUserID(login_session['email'])
	if not user_id:
		user_id = createUser(login_session)
	login_session['user_id'] = user_id

	output = ''
	output += '<h1>Welcome, '
	output += login_session['username']
	output += '!</h1>'
	output += '<img src="'
	output += login_session['picture']
	output += ' " style = width: 300px; height: 300px; border-redius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;">'
	print "Logged in."
	return output

# Route to logout of google account
@app.route('/gdisconnect')
def gdisconnect():
	access_token = login_session.get('access_token')
	if access_token is None:
		print 'Access Token is None'
		response = make_response(json.dumps('Current user not connected.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	print 'In gdisconnect access token is %s', access_token
	print 'User name is: '
	print login_session['username']
	url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
	h = httplib2.Http()
	result = h.request(url, 'GET')[0]
	print 'result is '
	print result
	# if user is logged into google account, log them out
	if result['status'] == '200':
		del login_session['access_token']
		del login_session['gplus_id']
		del login_session['username']
		del login_session['email']
		del login_session['picture']
		del login_session['provider']
		flash("You have been logged out.")
		return redirect(url_for('bookList'))
	else:
		response = make_response(json.dumps('Failed to revoke token for given user.'), 400)
		response.headers['Content-Type'] = 'application.json'
		return response

# Route for a new user to signup for permission to user app. Email Confirmation will be sent to them.
@app.route('/login/newUser', methods = ['GET', 'POST'])
def newUser():
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(8))
	login_session['state'] = state
	users = session.query(User)
	print state
	if request.method == 'POST':
		email = request.form['email']
		password = request.form['password']
		passwordConfirm = request.form['passwordConfirm']
		username = request.form['username']
		picture = request.form['picture']
		sender = "billfk1989@gmail.com"
		text = "This is your Authorization Code: "
		subject = "Authorization Code"
		for user in users:
			if email == user.email:
				flash("Email already in use, try a new email.")
				return redirect(url_for("newUser"))
			if username == user.name:
				flash("Username already in use, try a different one.")
				return redirect(url_for("newUser"))
		print password
		print "2 password: %s" % passwordConfirm
		if password == passwordConfirm:
			print "Password check passed"
			app.config['MAIL_SERVER'] = "smtp.gmail.com"
			app.config['MAIL_PORT'] = 465
			app.config['MAIL_USERNAME'] = 'billfk1989@gmail.com'
			app.config['MAIL_PASSWORD'] = '9223Tutwiler'
			app.config['MAIL_USE_TLS'] = False
			app.config['MAIL_USE_SSL'] = True
			mail = Mail(app)
			msg = Message(subject, sender = sender, recipients = [email])
			msg.body = "Your Authorization Code is: %s" % state
			mail.send(msg)
			print 'Email Sent'
			login_session['email'] = email
			login_session['username'] = username
			login_session['picture'] = picture
			login_session['password'] = password
			return redirect(url_for('newUserAuth'))
		else:
			flash("Your Password and Confirmation Password didn't match. Please try again.")
			return redirect(url_for("newUser"))
	else:
		return render_template('newUser.html')

# Route for new user to enter in their Authoriztion code that was emailed to them
@app.route('/login/newUserAuth', methods = ['GET', 'POST'])
def newUserAuth():
	if request.method == 'POST':
		if login_session['state'] == request.form['authCode']:
			user_id = getUserID(login_session['email'])
			if not user_id:
				user_id = createUser(login_session)
			login_session['user_id'] = user_id
			return redirect(url_for('bookList'))
		else:
			return "Wrong Authorization Code"
	else:
		return render_template('newUserAuth.html')

# Route for logging out of app
@app.route('/disconnect')
def disconnect():
	if login_session['state'] is None:
		print 'Login State is None'
		response = make_response(json.dumps('Current user not connected.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	if 'provider' in login_session:
		if login_session['provider'] == 'google':
			return redirect(url_for('gdisconnect'))
	print 'User email is: '
	print login_session.get('email')
	del login_session['username']
	del login_session['email']
	del login_session['picture']
	flash("You have been logged out.")
	return redirect(url_for('bookList'))

# Route for signing in to account that isn't google
@app.route('/signin', methods = ['GET', 'POST'])
def userSignin():
	if request.method == 'POST':
		email = request.form['email']
		password = request.form['password']
		user_id = getUserID(email)
		user = getUserInfo(user_id)
		if not user_id:
			return "User not Found."
		if password == user.password:
			login_session['user_id'] = user_id
			login_session['username'] = user.name
			login_session['email'] = user.email
			login_session['picture'] = user.picture
			flash("Welcome!")
			return redirect(url_for('userPage', user_id = user_id))
		else:
			flash("Incorrect Password")
			return redirect(url_for("userSignin"))
	else:
		return render_template('userSignin.html')

# Route for User information Page
@app.route('/userPage/<int:user_id>/', methods = ['GET', 'POST'])
def userPage(user_id):
	if 'username' not in login_session:
		flash("You must be logged in to access that page.")
		return redirect('/login')
	user = getUserInfo(user_id)
	books = session.query(Book)
	forums = session.query(Forum)
	for book in books:
		if book.user_id == user.id:
			print book.title
	for forum in forums:
		if forum.user_id == user.id:
			print forum.title
	return render_template('userInfoPage.html', user = user, books = books, forums = forums)

# Route for editing user information.
@app.route('/userPage/<int:user_id>/edit', methods = ['GET', 'POST'])
def editUser(user_id):
	if 'username' not in login_session:
		flash("You must be logged in to access that page.")
		return redirect('/login')
	user = getUserInfo(login_session['user_id'])
	editUser = session.query(User).filter_by(id = user_id).one()
	if login_session['user_id'] != editUser.id:
		return "You can't edit this user."
	if request.method == 'POST':
		if request.form['name']:
			editUser.name = request.form['name']
		if request.form['email']:
			editUser.email = request.form['email']
		if request.form['password']:
			editUser.password = request.form['password']
		if request.form['picture']:
			editUser.picture = request.form['picture']
		session.add(editUser)
		session.commit()
		return redirect(url_for('userPage', user_id = user_id))
	else:
		return render_template('editUser.html', user_id = user_id, editUser = editUser, user = user)

# Route for the list of forums and Creating a new forum
@app.route('/forumList/', methods = ['GET', 'POST'])
def forumList():
	if 'username' not in login_session:
		flash("You must be logged in to access that page.")
		return redirect('/login')
	user = getUserInfo(login_session['user_id'])
	forums = session.query(Forum)
	books = session.query(Book)
	if request.method == 'POST':
		forumSuggestionTitle = request.form['newForum']
		forumSuggestion_book_id = request.form.getlist('books')
		inUse = False
		for x in forumSuggestion_book_id:
			print x
		for forum in forums:
			if forumSuggestionTitle == forum.title:
				inUse = True
		if inUse == True:
			print "Name already in use"
		if inUse == False:
			newForum = Forum(title = forumSuggestionTitle,
				user_id = login_session['user_id'])
			#user_id = login_session['user_id'])
			session.add(newForum)
			session.commit()
			for x in forumSuggestion_book_id:
				newBookForumConnect = BookForumConnect(book_id = x, forum_id = newForum.id)
				session.add(newBookForumConnect)
				session.commit()
	return render_template('forumList.html', forums = forums, books = books, user = user)

# Route for viewing a particular forum and posting to it
@app.route('/forums/<int:forum_id>/', methods = ['GET', 'POST'])
def forum(forum_id, book_id = None):
	if 'username' not in login_session:
		flash("You must be logged in to access that page.")
		return redirect('/login')
	user = getUserInfo(login_session['user_id'])
	forum = session.query(Forum).filter_by(id = forum_id).one()
	forumPosts = session.query(ForumContent).filter_by(forum_id = forum.id)
	user_id = login_session['user_id']
	#userName = session.query(User).filter_by(id = forumPost.user_id)
	users = session.query(User)
	name = ""
	if request.method == 'POST':
		newPost = ForumContent(content =request.form['content'],
			time = datetime.datetime.now(),
			forum_id = forum_id,
			user_id = user_id)
		session.add(newPost)
		session.commit()
	return render_template('forum.html', forum = forum, forumPosts = forumPosts, users = users, name = name, user = user)

# Route for deleteing a forum
@app.route('/forums/<int:forum_id>/delete', methods = ['GET', 'POST'])
def deleteForum(forum_id):
	if 'username' not in login_session:
		flash("You must be logged in to access that page.")
		return redirect('/login')
	user = getUserInfo(login_session['user_id'])
	forumToDelete = session.query(Forum).filter_by(id = forum_id).one()
	print forumToDelete.user_id
	if login_session['user_id'] != forumToDelete.user_id:
		flash("Only the creator of a forum can delete it.")
		return redirect(url_for('forumList'))
	if request.method == 'POST':
		session.delete(forumToDelete)
		session.commit()
		return redirect(url_for('forumList'))
	else:
		return render_template('deleteForum.html', forumToDelete = forumToDelete, user = user)

# Route to show all the forums connected to a certain book
@app.route('/forumList/<int:book_id>/', methods = ['GET', 'POST'])
def bookForumList(book_id):
	if 'username' not in login_session:
		flash("You must be logged in to access that page.")
		return redirect('/login')
	user = getUserInfo(login_session['user_id'])
	forums = session.query(Forum).join(BookForumConnect).filter(BookForumConnect.book_id == book_id)
	book = session.query(Book).filter_by(id = book_id).one()
	return render_template('bookForumList.html', forums = forums, book = book, user = user)

# Return a ID if the email belongs to a user
def getUserID(email):
	try:
		user = session.query(User).filter_by(email = email).one()
		return user.id
	except:
		return None

# Returns a user object associated with this ID
def getUserInfo(user_id):
	try:
		user = session.query(User).filter_by(id = user_id).one()
		return user
	except:
		return None

#Create a new user in database
def createUser(login_session):
	newUser = User(name = login_session['username'],
		email = login_session['email'],
		picture = login_session['picture'],
		password = login_session['password'])
	session.add(newUser)
	session.commit()
	user = session.query(User).filter_by(email = login_session['email']).one()
	return user.id
	

if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)