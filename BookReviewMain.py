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

# Route for individual book information
@app.route('/books/<int:book_id>/')
def bookInformation(book_id):
	book = session.query(Book).filter_by(id = book_id).one()
	return render_template('bookinfo.html', book = book)

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
		session.add(editBook)
		session.commit()
		return redirect(url_for('bookInformation', book_id = book_id))
	else:
		return render_template('editBook.html', book_id = book_id, editBook = editBook)

# Route for deleting book information
@app.route('/books/<int:book_id>/delete', methods = ['GET', 'POST'])
def deleteBook(book_id):
	bookToDelete = session.query(Book).filter_by(id = book_id).one()
	if request.method == 'POST':
		session.delete(bookToDelete)
		session.commit()
		return redirect(url_for('bookList'))
	else:
		return render_template('deleteBook.html', bookToDelete = bookToDelete)

@app.route('/login')
def login():
	output = ''
	output += 'Page for logging in throught website'
	return output



	

if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)