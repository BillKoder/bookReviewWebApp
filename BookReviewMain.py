from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from BookReviewDatabase import Base, User, Book

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
	return render_template('bookList.html', books = books)
	#output = ''
	#output += '<h1>Books</h1>'
	#for book in books:
	#	output += book.title
	#	output += '</br>'
	#return output

# Route for individual book information
@app.route('/books/<int:book_id>/')
def bookInformation(book_id):
	book = session.query(Book).filter_by(id = book_id).one()
	return render_template('bookinfo.html', book = book)

	#output = ''
	#for book in books:
	#	output += '<h1>'
	#	output += book.title
	#	output += '</h1>'
	#	output += 'Author: ' + str(book.author)
	#	if book.subject is not None:
	#		output += 'Subject: ' + str(book.subject)
	#	if book.category is not None:
	#		output += 'Category: ' + str(book.category)
	#	if book.summary is not None:
	#		output += 'Summary; ' + str(book.summary)
	#	output += '</br>'
	#return output


# Route for adding a new book
@app.route('/books/new', methods = ['GET', 'POST'])
def newBook():
	if request.method == 'POST':
		newBook = Book(title = request.form['title'],
			author = request.form['author'],
			subject = request.form['subject'],
			category = request.form['category'],
			summary = request.form['summary'])
		session.add(newBook)
		session.commit()
		return redirect(url_for('bookList'))
	else:
		return render_template('newBook.html')



# Route for editing book information
@app.route('/books/<int:book_id>/edit', methods = ['GET', 'POST'])
def editBook(book_id):
	editBook = session.query(Book).filter_by(id = book_id).one()
	output = ''
	output += 'Page for editing information of ' + str(editBook.title)
	return output

# Route for deleting book information
@app.route('/books/<int:book_id>/delete', methods = ['GET', 'POST'])
def deleteBook(book_id):
	deleteBook = session.query(Book).filter_by(id = book_id).one()
	output = ''
	output += 'Page for deleting ' + str(deleteBook.title)
	return output

@app.route('/login')
def login():
	output = ''
	output += 'Page for logging in throught website'
	return output



	

if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)